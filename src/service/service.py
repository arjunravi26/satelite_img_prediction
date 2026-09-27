from src.prediction.model import Model
from src.utils.read_config import read_config
from src.preprocessing.preprocessing import preprocess_image
from src.db.prediction_db import DB
import torch


class Service:
    def __init__(self):
        self.prob_threshold = read_config("prob_threshold")
        self.margin_threshold = read_config("margin_threshold")
        self.model = Model()
        self.db = DB()

    def predict(self, img_name, img):
        try:
            data = preprocess_image(X=img)
            pred_idx, pred_probs = self.model.predict(X=data)

            pred_label, labels_probs = self._process_output(
                pred_cls=pred_idx, pred_probs=pred_probs)
            need_review, review_reason = self._verify_output(
                pred_probs=pred_probs)
            self._insert_into_db(img_name=img_name, predicted_cls=pred_label,
                                 pred_cls_prob=float(pred_probs[0][pred_idx]), prob=labels_probs, need_review=need_review, review_reason=review_reason)
            return pred_label
        except Exception as e:
            raise

    def _process_output(self, pred_cls, pred_probs):
        try:
            no_of_classes = read_config("no_of_classes")
            labels = read_config("labels")

            pred_idx = int(pred_cls.item())
            if not 0 <= pred_idx < no_of_classes:
                raise ValueError(
                    f"Invalid predicted class index: {pred_idx}"
                )
            idx_to_label = read_config("idx_to_label")
            labels_probs = self._create_prob_cls_dict(
                labels=labels, pred_probs=pred_probs)
            return idx_to_label[pred_cls[0].item()], labels_probs
        except Exception as e:
            raise

    def _create_prob_cls_dict(self, labels, pred_probs):

        return {label: prob.item() for label, prob in zip(labels, pred_probs[0])}

    def _verify_output(self, pred_probs):
        try:

            probs = pred_probs.squeeze(0)
            top_probs = torch.topk(probs, k=2).values
            p1, p2 = top_probs.tolist()

            low_confidence = p1 < self.prob_threshold
            low_margin = p1 - p2 < self.margin_threshold
            need_review = low_confidence or low_margin

            if low_margin and low_confidence:
                review_reason = "both"
            elif low_margin:
                review_reason = "low_margin"
            elif low_confidence:
                review_reason = "low_confidence"
            else:
                review_reason = None
            return need_review, review_reason

        except Exception as e:
            raise

    def _insert_into_db(self, img_name,
                        predicted_cls,
                        pred_cls_prob,
                        prob,
                        need_review,
                        review_reason,
                        ):
        try:

            model_version = read_config("model_version")
            self.db.insert_prediction(img_name=img_name, img_path="", predicted_cls=predicted_cls, pred_cls_prob=pred_cls_prob,
                                      prob=prob, need_review=need_review, review_reason=review_reason, review_status=0, model_version=model_version,)
        except Exception as e:
            raise
