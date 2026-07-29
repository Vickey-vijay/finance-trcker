"""Local quantized LLM runner (llama.cpp backend).

Loads a GGUF chat model once per process through llama-cpp-python and answers
short prompts on CPU. Every failure path returns an empty string or False so
the web application never depends on the model being present, fully
downloaded, or loadable in the available memory.
"""
import atexit
import os
from pathlib import Path

import requests

from config import Config

MODEL_REPO = Config.LOCAL_MODEL_REPO
MODEL_FILE = Config.LOCAL_MODEL_FILE
MODEL_DIR = Path(Config.MODEL_DIR)
MODEL_PATH = MODEL_DIR / MODEL_FILE

_DOWNLOAD_URL = f"https://huggingface.co/{MODEL_REPO}/resolve/main/{MODEL_FILE}"
_CHUNK = 1024 * 1024

_llm = None
_LLAMA_CPP_OK = None


# --------------------------------------------------------------------------- #
#  Availability
# --------------------------------------------------------------------------- #
def _llama_cpp_importable():
    global _LLAMA_CPP_OK
    if _LLAMA_CPP_OK is None:
        try:
            import llama_cpp  # noqa: F401
            _LLAMA_CPP_OK = True
        except Exception:
            _LLAMA_CPP_OK = False
    return _LLAMA_CPP_OK


def model_downloaded() -> bool:
    return MODEL_PATH.is_file() and MODEL_PATH.stat().st_size > 0


def is_available() -> bool:
    """Cheap check only: never loads the model into memory."""
    return _llama_cpp_importable() and model_downloaded()


# --------------------------------------------------------------------------- #
#  Download
# --------------------------------------------------------------------------- #
def download_model(progress_cb=None) -> bool:
    """Stream the GGUF from Hugging Face to MODEL_PATH.

    Writes to a `.part` file first and renames it into place only once the
    downloaded size matches the server's content-length, so a reader can
    never observe a half-written model file. A leftover `.part` from an
    earlier interrupted run is always discarded and the download restarted,
    since a plain GET cannot be resumed with a byte-accurate offset.
    """
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    part_path = MODEL_PATH.with_name(MODEL_PATH.name + ".part")

    try:
        head = requests.head(_DOWNLOAD_URL, allow_redirects=True, timeout=30)
        head.raise_for_status()
        total = int(head.headers.get("content-length", 0))
    except Exception:
        total = 0

    if part_path.exists():
        if not total or part_path.stat().st_size != total:
            try:
                part_path.unlink()
            except OSError:
                pass

    try:
        downloaded = 0
        last_report = 0
        with requests.get(_DOWNLOAD_URL, stream=True, timeout=Config.LLM_TIMEOUT) as r:
            r.raise_for_status()
            if not total:
                total = int(r.headers.get("content-length", 0))
            with open(part_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=_CHUNK):
                    if not chunk:
                        continue
                    f.write(chunk)
                    downloaded += len(chunk)
                    if progress_cb and downloaded - last_report >= _CHUNK:
                        progress_cb(downloaded, total)
                        last_report = downloaded
        if progress_cb:
            progress_cb(downloaded, total)
        if total and downloaded != total:
            part_path.unlink(missing_ok=True)
            return False
        os.replace(part_path, MODEL_PATH)
        return True
    except Exception:
        return False


# --------------------------------------------------------------------------- #
#  Inference
# --------------------------------------------------------------------------- #
def _load():
    global _llm
    if _llm is not None:
        return _llm
    if not is_available():
        return None
    try:
        from llama_cpp import Llama
        _llm = Llama(
            model_path=str(MODEL_PATH),
            n_ctx=Config.LOCAL_MODEL_CTX,
            n_threads=Config.LOCAL_MODEL_THREADS,
            verbose=False,
        )
    except Exception:
        _llm = None
    return _llm


def generate(prompt, system="", max_tokens=512, temperature=0.3, stop=None) -> str:
    """Run one chat completion. Returns "" on any failure, including OOM."""
    llm = _load()
    if llm is None:
        return ""
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    try:
        out = llm.create_chat_completion(
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
            stop=stop,
        )
        return out["choices"][0]["message"]["content"].strip()
    except Exception:
        return ""


def status() -> dict:
    ready = is_available()
    size_mb = round(MODEL_PATH.stat().st_size / (1024 * 1024), 1) if MODEL_PATH.exists() else 0.0
    if ready:
        detail = "Qwen2.5 1.5B (Q4_K_M) running locally"
    elif model_downloaded() and not _llama_cpp_importable():
        detail = "Model file present but llama-cpp-python is not installed"
    elif not model_downloaded():
        detail = "Local model not downloaded yet"
    else:
        detail = "Local model unavailable"
    return {"backend": "llama.cpp", "model": MODEL_FILE, "quantization": "Q4_K_M",
            "ready": ready, "detail": detail, "size_mb": size_mb}


def unload() -> None:
    global _llm
    if _llm is not None:
        try:
            _llm.close()
        except Exception:
            pass
    _llm = None


# llama.cpp holds native memory that has to be handed back while the interpreter
# is still intact. Left to the garbage collector it is freed during shutdown,
# after the ctypes bindings have already been torn down, which prints an
# alarming but harmless traceback. Releasing it here keeps process exit clean.
atexit.register(unload)


if __name__ == "__main__":
    if model_downloaded():
        print(f"{MODEL_FILE}: already downloaded (100%)")
    else:
        def _report(done, total):
            pct = (done / total * 100) if total else 0.0
            print(f"\rDownloading {MODEL_FILE}: {pct:5.1f}%", end="", flush=True)

        ok = download_model(_report)
        print()
        print("Download complete." if ok else "Download failed.")
