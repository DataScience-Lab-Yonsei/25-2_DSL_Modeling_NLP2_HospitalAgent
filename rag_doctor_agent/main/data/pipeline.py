from __future__ import annotations
import os, glob, json, shutil
from typing import List, Dict, Any
from dotenv import load_dotenv

load_dotenv()

RAG_DATA_DIR = os.getenv("RAG_DATA_DIR",
                         os.path.join(os.path.dirname(__file__), "..", "data"))
RAW_DIR  = os.path.join(RAG_DATA_DIR, "raw_data")
DB_DIR   = os.path.join(RAG_DATA_DIR, "db_data")
PREPROC_DIR = os.path.join(DB_DIR, "preprocessed")
INDEX_DIR   = os.path.join(DB_DIR, "index")

from .loaders import load_file_to_docs

# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
def _ensure_dirs() -> None:
    os.makedirs(RAW_DIR, exist_ok=True)
    os.makedirs(DB_DIR, exist_ok=True)
    os.makedirs(PREPROC_DIR, exist_ok=True)
    os.makedirs(INDEX_DIR, exist_ok=True)

def init() -> None:
    """폴더 구조만 생성"""
    _ensure_dirs()
    for d, note in [
        (RAW_DIR,      "# Put raw files (csv/xlsx/…) here\n"),
        (PREPROC_DIR,  "# Auto-generated preprocessed JSONL will appear here\n"),
        (DB_DIR,       "# Only files inside this folder are indexed.\n")
    ]:
        p = os.path.join(d, "README.md")
        if not os.path.exists(p):
            with open(p, "w", encoding="utf-8") as f:
                f.write(note)
    print(json.dumps({"ok": True, "RAG_DATA_DIR": RAG_DATA_DIR}, ensure_ascii=False))

# --------------------------------------------------------------------------- #
# Pipeline steps
# --------------------------------------------------------------------------- #
def prepare() -> None:
    """raw_data → db_data/preprocessed 로 전처리(JSONL)"""
    _ensure_dirs()

    # raw_data 안의 모든 파일 + (초기 호환) /mnt/data 경로 자동 감지
    raw_files = sorted(glob.glob(os.path.join(RAW_DIR, "*")))
    if not raw_files:
        raw_files = [p for p in ["/mnt/data/medical_team_info.xlsx",
                                 "/mnt/data/barunjoint_symptoms.csv"]
                     if os.path.exists(p)]

    used, total_docs = [], 0
    for fp in raw_files:
        docs = load_file_to_docs(fp)
        if not docs:
            continue
        base = os.path.splitext(os.path.basename(fp))[0]
        outp = os.path.join(PREPROC_DIR, f"{base}.jsonl")
        with open(outp, "w", encoding="utf-8") as f:
            for d in docs:
                f.write(json.dumps(d, ensure_ascii=False) + "\n")
        total_docs += len(docs)
        used.append(fp)

    print(json.dumps(
        {"ok": True, "prepared_docs": total_docs, "files": used},
        ensure_ascii=False))

def index() -> None:
    """
    db_data/** 내 *.json / *.jsonl 만 인덱싱.
    (raw_data 파일은 절대 인덱싱하지 않음)
    """
    _ensure_dirs()

    preproc  = sorted(glob.glob(os.path.join(PREPROC_DIR, "*.jsonl")))
    roots    = sorted(glob.glob(os.path.join(DB_DIR, "*.json")))   \
             + sorted(glob.glob(os.path.join(DB_DIR, "*.jsonl")))

    staging = os.path.join(DB_DIR, "all_docs.jsonl")
    cnt = 0
    with open(staging, "w", encoding="utf-8") as out:
        for path in preproc + roots:
            # ▶▶ 절대/상대 경로 섞임 문제 해결 ◀◀
            if os.path.commonpath(
                    [os.path.abspath(DB_DIR), os.path.abspath(path)]
                ) != os.path.abspath(DB_DIR):
                # db_data 바깥 파일은 무시
                continue

            with open(path, "r", encoding="utf-8") as f:
                if path.endswith(".jsonl"):
                    for line in f:
                        out.write(line if line.endswith("\n") else line + "\n")
                        cnt += 1
                else:  # .json
                    data = json.load(f)
                    items = data if isinstance(data, list) else data.get("docs", [])
                    for d in items:
                        out.write(json.dumps(d, ensure_ascii=False) + "\n")
                        cnt += 1

    # 실제 VectorDB 인덱스 빌드
    from ..agent.retriever import Retriever
    info = Retriever().ingest_from_db_data()
    print(json.dumps(
        {"ok": True,
         "docs_indexed": info.get("counts", {}).get("docs", 0)},
        ensure_ascii=False))

def build() -> None:
    """init + prepare + index 한 번에"""
    init()
    prepare()
    index()

def show() -> None:
    meta = os.path.join(INDEX_DIR, "index_meta.json")
    m = json.load(open(meta, "r", encoding="utf-8")) if os.path.exists(meta) else {}
    print(json.dumps(
        {"RAG_DATA_DIR": RAG_DATA_DIR, "index_meta": m},
        ensure_ascii=False))

def clean() -> None:
    if os.path.exists(INDEX_DIR):
        for fn in os.listdir(INDEX_DIR):
            try: os.remove(os.path.join(INDEX_DIR, fn))
            except Exception: pass
    print(json.dumps({"ok": True, "cleaned": INDEX_DIR}, ensure_ascii=False))

# --------------------------------------------------------------------------- #
# CLI 엔트리
# --------------------------------------------------------------------------- #
def main() -> None:
    import sys
    if len(sys.argv) < 2:
        print("Usage: python -m rag_doctor_agent.data.pipeline "
              "[init|prepare|index|build|show|clean]")
        return
    cmd = sys.argv[1]
    {"init":    init,
     "prepare": prepare,
     "index":   index,
     "build":   build,
     "show":    show,
     "clean":   clean}.get(cmd, lambda: print("Unknown command:", cmd))()

if __name__ == "__main__":
    main()
