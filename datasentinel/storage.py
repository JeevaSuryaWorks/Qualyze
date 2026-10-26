from pathlib import Path
import json
from datetime import datetime, timezone
from sqlalchemy import create_engine, text

DB_PATH = Path(__file__).resolve().parents[1] / "datasentinel_history.db"
engine = create_engine(f"sqlite:///{DB_PATH}", future=True)

def init_db():
    with engine.begin() as conn:
        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS audits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_name TEXT NOT NULL,
            row_count INTEGER NOT NULL,
            column_count INTEGER NOT NULL,
            finding_count INTEGER NOT NULL,
            quality_score INTEGER NOT NULL,
            created_at TEXT NOT NULL,
            findings_json TEXT NOT NULL
        )
        """))

def save_audit(source_name, summary, findings):
    with engine.begin() as conn:
        result = conn.execute(text("""
            INSERT INTO audits (source_name, row_count, column_count, finding_count, quality_score, created_at, findings_json)
            VALUES (:source, :rows, :cols, :count, :score, :created, :findings)
        """), {
            "source": str(source_name), "rows": int(summary["rows"]),
            "cols": int(summary["columns"]), "count": int(summary["finding_count"]),
            "score": int(summary["quality_score"]),
            "created": datetime.now(timezone.utc).isoformat(),
            "findings": json.dumps(findings, ensure_ascii=False)
        })
        return result.lastrowid

def recent_audits(limit=25):
    with engine.connect() as conn:
        rows = conn.execute(text("""
            SELECT id, source_name, row_count, column_count, finding_count, quality_score, created_at
            FROM audits ORDER BY id DESC LIMIT :limit
        """), {"limit": int(limit)}).mappings().all()
    return [dict(r) for r in rows]
