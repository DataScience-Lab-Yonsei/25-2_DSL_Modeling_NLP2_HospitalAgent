from __future__ import annotations
from typing import List, Dict, Any
import os, json, pandas as pd
from ..agent.utils import normalize_text
from ..agent.augmentation import canonical_title

# ---- Normalizers (shared with legacy) ----
def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    mapping = {}
    for c in df.columns:
        cl = normalize_text(str(c))
        if any(k in cl for k in ["의료진", "의사", "doctor", "name", "성명"]):
            mapping[c] = "doctor_name"
        elif any(k in cl for k in ["진료과", "과", "department", "dept", "센터"]):
            mapping[c] = "dept"
        elif any(k in cl for k in ["직함", "title", "position", "role"]):
            mapping[c] = "title"
        elif any(k in cl for k in ["전문", "전공", "special", "subspecial"]):
            mapping[c] = "specialty"
        elif any(k in cl for k in ["가능", "진료", "증상", "treat", "condition"]):
            mapping[c] = "treats"
        else:
            mapping[c] = c
    out = df.copy()
    out.columns = [mapping[c] for c in df.columns]
    return out

# ---- Builders ----
def build_docs_from_team(df: pd.DataFrame, source: str) -> List[Dict[str, Any]]:
    docs = []
    def cell_to_str(v):
        import pandas as pd
        if isinstance(v, pd.Series):
            vals = [str(x) for x in v.values if str(x) != 'nan']
            vals = list(dict.fromkeys([x.strip() for x in vals if x.strip()]))
            return "/".join(vals)
        return str(v)
    for i, row in df.iterrows():
        dn = cell_to_str(row.get("doctor_name", "")).strip()
        dp = cell_to_str(row.get("dept", "")).strip()
        tl = canonical_title(cell_to_str(row.get("title", "")).strip() or "")
        sp = cell_to_str(row.get("specialty", "")).strip()
        tr = cell_to_str(row.get("treats", "")).strip()
        meta = {"doctor_name": dn, "dept": dp, "title": tl, "specialty": sp, "treats": tr}
        parts = [dn, dp, tl, sp, tr]
        text = " | ".join([p for p in parts if p and p != 'nan'])
        if not text: 
            continue
        docs.append({"id": f"{os.path.basename(source)}-team-{i}", "text": text, "meta": meta, "source": source, "type": "team"})
    return docs

def build_docs_from_symptom(df: pd.DataFrame, source: str) -> List[Dict[str, Any]]:
    docs = []
    for i, row in df.iterrows():
        sym = str(row.get("symptom", row.get("symptoms", row.get("keyword", row.get("증상", ""))))).strip()
        dept = str(row.get("dept", row.get("department", row.get("진료과", "")))).strip()
        note = str(row.get("note", row.get("설명", row.get("reason", "")))).strip()
        if not sym and not dept:
            text = " | ".join([str(x) for x in row.values if str(x) != 'nan'])
            meta = {"raw": {k: str(v) for k, v in row.to_dict().items()}}
        else:
            meta = {"symptom": sym, "dept": dept, "note": note}
            text = " | ".join([sym, dept, note])
        docs.append({"id": f"{os.path.basename(source)}-sym-{i}", "text": text, "meta": meta, "source": source, "type": "symptom"})
    return docs

# ---- Loader registry ----
def load_file_to_docs(path: str) -> List[Dict[str, Any]]:
    p = path.lower()
    try:
        if p.endswith(".csv"):
            df = pd.read_csv(path)
            df = normalize_columns(df)
            # heuristic: detect if team vs symptom by column presence
            if "doctor_name" in df.columns and "dept" in df.columns:
                return build_docs_from_team(df, path)
            else:
                return build_docs_from_symptom(df, path)
        elif p.endswith(".xlsx") or p.endswith(".xls"):
            xls = pd.ExcelFile(path)
            best = None
            for sh in xls.sheet_names:
                df = xls.parse(sh)
                if best is None or (df.shape[1] > best.shape[1] and df.shape[0] >= best.shape[0]):
                    best = df
            df = normalize_columns(best)
            if "doctor_name" in df.columns and "dept" in df.columns:
                return build_docs_from_team(df, path)
            else:
                return build_docs_from_symptom(df, path)
        elif p.endswith(".jsonl"):
            docs = []
            with open(path, "r", encoding="utf-8") as f:
                for line in f:
                    d = json.loads(line)
                    # ensure required fields
                    d.setdefault("id", f"{os.path.basename(path)}-{len(docs)}")
                    d.setdefault("text", "")
                    d.setdefault("meta", {})
                    d.setdefault("source", path)
                    d.setdefault("type", d.get("type", "external"))
                    docs.append(d)
            return docs
        elif p.endswith(".json"):
            payload = json.load(open(path, "r", encoding="utf-8"))
            docs = []
            if isinstance(payload, list):
                for i, d in enumerate(payload):
                    d.setdefault("id", f"{os.path.basename(path)}-{i}")
                    d.setdefault("text", "")
                    d.setdefault("meta", {})
                    d.setdefault("source", path)
                    d.setdefault("type", d.get("type", "external"))
                    docs.append(d)
            elif isinstance(payload, dict) and "docs" in payload:
                for i, d in enumerate(payload["docs"]):
                    d.setdefault("id", f"{os.path.basename(path)}-{i}")
                    d.setdefault("text", "")
                    d.setdefault("meta", {})
                    d.setdefault("source", path)
                    d.setdefault("type", d.get("type", "external"))
                    docs.append(d)
            return docs
        else:
            return []
    except Exception as e:
        # Skip problematic file but continue pipeline
        return []
