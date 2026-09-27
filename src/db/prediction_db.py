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

    def search_predictions(
        self,
        predicted_cls=None,
        min_confidence=None,
        max_confidence=None,
        need_review=None,
        review_status=None,
        model_version=None,
        limit=100,
    ):

        try:
            conditions = []
            params = []

            if predicted_cls is not None:
                conditions.append("predicted_cls = ?")
                params.append(predicted_cls)

            if min_confidence is not None:
                conditions.append("pred_cls_prob >= ?")
                params.append(min_confidence)

            if max_confidence is not None:
                conditions.append("pred_cls_prob <= ?")
                params.append(max_confidence)

            if need_review is not None:
                conditions.append("need_review = ?")
                params.append(int(need_review))

            if review_status is not None:
                conditions.append("review_status = ?")
                params.append(review_status)

            if model_version is not None:
                conditions.append("model_version = ?")
                params.append(model_version)

            query = """
                   SELECT
                       id,
                       img_name,
                       img_path,
                       predicted_cls,
                       pred_cls_prob,
                       prob,
                       need_review,
                       review_reason,
                       review_status,
                       model_version,
                       created_at
                   FROM predictions
               """

            if conditions:
                query += " WHERE " + " AND ".join(conditions)

            query += """
                   ORDER BY created_at DESC
                   LIMIT ?
               """

            params.append(limit)
            rows = self.cur.execute(query, params).fetchall()
            return [row for row in rows]

        except Exception as e:
            raise

    def close(self):
        self.conn.close()
