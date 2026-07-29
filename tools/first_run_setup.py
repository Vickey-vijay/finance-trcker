"""Prepares everything the application needs before its first launch.

Run once by setup.bat, and safe to run again at any time. Each step reports
its own state so a re-run only does the work that is still outstanding:

  1. create the .env settings file from the template
  2. download the quantized language model that runs on this machine
  3. cache the sentence-embedding model used by the chatbot's retrieval step
  4. make sure the transaction classifier has a trained model to load
  5. create the database tables
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)


def step(number, title):
    print(f"\n[{number}/5] {title}")


def create_env_file():
    env_path = os.path.join(ROOT, ".env")
    template = os.path.join(ROOT, ".env.example")
    if os.path.exists(env_path):
        print("      Settings file already present.")
        return
    if not os.path.exists(template):
        print("      Settings template missing; using built-in defaults.")
        return
    with open(template, encoding="utf8") as src:
        content = src.read()
    with open(env_path, "w", encoding="utf8") as dst:
        dst.write(content)
    print("      Settings file created.")


def fetch_language_model():
    try:
        import llm_local
    except Exception as exc:
        print(f"      Skipped: {exc}")
        return
    if llm_local.model_downloaded():
        print(f"      Already present ({llm_local.status()['size_mb']:.0f} MB).")
        return

    last = [-1]

    def report(done, total):
        pct = int(done / total * 100) if total else 0
        if pct != last[0]:
            last[0] = pct
            bar = "#" * (pct // 4) + "-" * (25 - pct // 4)
            print(f"\r      [{bar}] {pct:3d}%   ", end="", flush=True)

    print("      Downloading (about 1 GB, this is the longest step)...")
    ok = llm_local.download_model(report)
    print()
    print("      Done." if ok else "      Could not download. The app will still run "
                                   "using its built-in advisor.")


def cache_embedding_model():
    try:
        from sentence_transformers import SentenceTransformer
    except Exception:
        print("      Not installed; the chatbot will use keyword search instead.")
        return
    try:
        SentenceTransformer("all-MiniLM-L6-v2").encode("warm up")
        print("      Ready.")
    except Exception as exc:
        print(f"      Could not cache the model ({exc}). Keyword search will be used.")


def prepare_classifier():
    try:
        import classifier
    except Exception as exc:
        print(f"      Skipped: {exc}")
        return
    if classifier.model_ready():
        print("      Trained model found.")
        return
    try:
        result = classifier.train_model()
        print(f"      Trained on {result['samples']} examples "
              f"(accuracy {result['accuracy'] * 100:.1f}%).")
    except Exception as exc:
        print(f"      Rule engine only ({exc}).")


def prepare_database():
    try:
        from app import app
        from models import db, ensure_schema
        with app.app_context():
            db.create_all()
            ensure_schema(db.engine)
        print("      Database ready.")
    except Exception as exc:
        print(f"      Will be created on first launch ({exc}).")


def main():
    print("=" * 60)
    print("  SmartEdit AI - preparing your installation")
    print("=" * 60)
    step(1, "Settings file")
    create_env_file()
    step(2, "On-device language model")
    fetch_language_model()
    step(3, "Transaction embedding model")
    cache_embedding_model()
    step(4, "Transaction classifier")
    prepare_classifier()
    step(5, "Database")
    prepare_database()
    print("\n" + "=" * 60)
    print("  Ready. Close this window and double-click run.bat")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
