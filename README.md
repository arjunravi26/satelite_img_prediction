# GalaxEye Classifier — Offline Satellite Tile Classification (Take-Home)

A small offline service that classifies satellite image tiles using a locally-trained CNN Model,
stores each result with a confidence-based information, and exposes a predict endpoint for classification.

This is Part 2 of the take-home assignment: a basic working slice of the design
described in [`DESIGN_NOTE.pdf`](./docs/DESIGN_NOTE.pdf).

## Architecture

```
API (FastAPI) → Service → Preprocessing → Model → Post-processing
                                              ↓
                                       Decision Layer (confidence + margin)
                                              ↓
                                       SQLite (predictions.db)
```

- **`main.py`** — FastAPI app, lifespan-managed model/DB startup, mounts router.
- **`api/v1/predict_router.py`** — `POST /predict`: accepts one image, validates type/size, runs inference.
- **`src/service/service.py`** — orchestrates preprocess → predict → post-process → decision layer → DB insert.
- **`src/prediction/`** — model architecture (`layers.py`) and inference wrapper (`model.py`).
- **`src/preprocessing/preprocessing.py`** — image → tensor, scale pixel.
- **`src/db/prediction_db.py`** — SQLite schema and insert data.
- **`db_data/prediction.db`** — database file.
- **`config/config.yaml`** — class labels, model weights path, thresholds, DB path.
- **`experiment/sat_img_classifier.ipynb`** — training notebook (CNN trained from scratch on the provided tiles).
- **`models/`** — trained weight checkpoints.

## Model

A small CNN(≈0.4M Parameter) (4 conv blocks + global average pool + linear head) trained from
scratch in `experiment/sat_img_classifier.ipynb` on the provided tile dataset. Test accuracy ≈ 66%.

## Setup

Requires Python 3.10+.

```bash
git clone https://github.com/arjunravi26/satelite_img_prediction.git
cd satelite_img_prediction
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Running

Run from the **repository root** (config paths are relative to it):

```bash
uvicorn main:app --reload
```

The app starts on `http://127.0.0.1:8000`, loads the model and opens the
SQLite DB (`db_data/predictions.db`) on startup.

- `http://127.0.0.1:8000/` — simple upload form for `/predict`

## API

### `POST /predict`

Accepts a single image (`png`), **must be exactly 64×64
px**. Runs preprocessing → CNN inference → decision layer, and stores the
result.

On Website
1. Go to: "http://127.0.0.1:8000/" (local ip address)
2. Upload Image
3. Click Submit

On Powershell
```bash
  curl.exe -X POST "http://127.0.0.1:8000/predict" -F "file=@{img_file_path}"
```

Response:
```json
{"result": "Result from model: Forest"}
```


## Decision layer (confidence handling)

Every prediction is stored — nothing is silently dropped. A prediction is
flagged `need_review = true` when either:
- top-1 probability is below `prob_threshold` (config, default `0.6`), or
- the margin between top-1 and top-2 probability is below `margin_threshold`
  (config, default `0.05`) — catching cases where the model is confidently
  torn between two classes, not just generally unsure.

`review_reason` records which condition fired: `low_confidence`,
`low_margin`, `both`, or `null`. See `DESIGN_NOTE.pdf` for the reasoning
behind using both signals.


## Part 3 — Problem-Solving Answers

See [`PART_3.pdf`](./docs/PART_3.pdf).
