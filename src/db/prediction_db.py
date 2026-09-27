import sqlite3
from src.utils.read_config import read_config
import json

try:
    db_path = read_config("db_path")
except Exception:
    raise


class DB:
    def __init__(self):
        self.conn = sqlite3.connect(db_path)
        self.cur = self.conn.cursor()
        self._create_table()

    def _create_table(self):

        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                img_name TEXT NOT NULL,
                img_path TEXT,
                predicted_cls TEXT NOT NULL,
                pred_cls_prob REAL NOT NULL,
                prob TEXT NOT NULL,
                need_review INTEGER  NOT NULL DEFAULT 0,
                review_reason TEXT,
                review_status TEXT,
                model_version TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        self.conn.commit()

    def insert_prediction(self,
                          img_name: str,
                          img_path: str,
                          predicted_cls: str,
                          pred_cls_prob: float,
                          prob: dict,
                          need_review: bool,
                          review_reason: str | None,
                          review_status: str | None,
                          model_version: str
                          ):

        prob_json = json.dumps(prob)

        self.cur.execute("""
            INSERT INTO predictions (
                img_name,
                img_path,
                predicted_cls,
                pred_cls_prob,
                prob,
                need_review,
                review_reason,
                review_status,
                model_version
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            img_name,
            img_path,
            predicted_cls,
            pred_cls_prob,
            prob_json,
            int(need_review),
            review_reason,
            review_status,
            model_version
        ))

        self.conn.commit()

        prediction_id = self.cur.lastrowid
        return prediction_id


    def close(self):
        self.conn.close()
