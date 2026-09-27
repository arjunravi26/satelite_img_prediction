from src.prediction.layers import model
from src.utils.read_config import read_config
import torch
import os
import time

class Model:
    def __init__(self):
        self.model: torch.nn.Module = model
        self._load_weights_to_model()

    def _load_weights_to_model(self):
        try:
            model_weights_path = read_config("model_weights_path")
            self._check_path_exists(path=model_weights_path)
            weight_dict = torch.load(model_weights_path)
            self.model.load_state_dict(weight_dict)
        except Exception as e:
            raise

    def _check_path_exists(self, path: str):
        if not os.path.exists(path=path):
            raise FileExistsError

    def predict(self, X: torch.Tensor):
        try:
            with torch.inference_mode():
                pred = self.model(X)
            pred_prob = torch.softmax(pred, dim=1)
            pred_class = torch.argmax(pred_prob, dim=1)
            return pred_class, pred_prob
        except Exception as e:
            raise
