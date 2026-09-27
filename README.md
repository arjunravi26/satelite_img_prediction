# GalaxEye Classifier — Offline Satellite Tile Classification (Take-Home)

A small offline service that classifies satellite image tiles by land-use type
using a locally-trained CNN, stores each result with a confidence-based
review flag, and exposes a query endpoint for an analyst to filter results.

This is Part 2 of the take-home assignment: a working slice of the design
described in `DESIGN_NOTE.md`, not a finished product. See
**Known Limitations** below for what's intentionally stubbed.

## Architecture

```
API (FastAPI) → Service → Preprocessing → Model → Post-processing
                                              ↓
                                       Decision Layer (confidence + margin)
                                              ↓
                                       SQLite (predictions.db)
```

- **`main.py`** — FastAPI app, lifespan-managed model/DB startup, mounts both routers.
- **`api/v1/predict_router.py`** — `POST /predict`: accepts one image, validates type/size, runs inference.
- **`api/v1/query_router.py`** — `GET /result`: filterable query over stored predictions.
- **`src/service/service.py`** — orchestrates preprocess → predict → post-process → decision layer → DB insert.
- **`src/prediction/`** — model architecture (`layers.py`) and inference wrapper (`model.py`).
- **`src/preprocessing/preprocessing.py`** — image → tensor.
- **`src/db/prediction_db.py`** — SQLite schema, insert, and filtered query.
- **`config/config.yaml`** — class labels, model weights path, thresholds, DB path.
- **`experiment/sat_img_classifier.ipynb`** — training notebook (CNN trained from scratch on the provided tiles).
- **`models/`** — trained weight checkpoints.

## Model

A small CNN (4 conv blocks + global average pool + linear head) trained from
scratch in `experiment/sat_img_classifier.ipynb` on the provided tile dataset
(7 classes: AnnualCrop, Forest, Highway, Industrial, Residential, River,
SeaLake). Test accuracy ≈ 66%. Accuracy isn't the point of this exercise —
see `DESIGN_NOTE.md` for why a small from-scratch CNN was chosen over a
pretrained model or an MLLM.

## Setup

Requires Python 3.10+.

```bash
git clone https://github.com/arjunravi26/satelite_img_prediction.git
cd satelite_img_prediction
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
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
- `http://127.0.0.1:8000/query` — simple filter form for `/result`
- `http://127.0.0.1:8000/docs` — interactive Swagger UI for both endpoints

## API

### `POST /predict`

Accepts a single image (`jpeg`, `png`, or `webp`), **must be exactly 64×64
px**. Runs preprocessing → CNN inference → decision layer, and stores the
result.

```bash
curl -X POST http://127.0.0.1:8000/predict \
  -F "file=@sample_tiles/Forest_12.png"
```

Response:
```json
{"result": "Result from model: Forest"}
```

### `GET /result`

Query stored predictions with optional filters.

| Param            | Type  | Notes                                   |
|-------------------|-------|------------------------------------------|
| `predicted_cls`   | str   | e.g. `Forest`                             |
| `min_confidence`  | float | 0.0–1.0, on top-1 class probability       |
| `max_confidence`  | float | 0.0–1.0                                   |
| `need_review`     | bool  | `true` = flagged for review               |
| `review_status`   | str   | see Known Limitations                     |
| `model_version`   | str   | e.g. `model_v0.0`                         |
| `limit`           | int   | default 100, max 1000                     |

```bash
curl "http://127.0.0.1:8000/result?need_review=true&limit=20"
```

## Decision layer (confidence handling)

Every prediction is stored — nothing is silently dropped. A prediction is
flagged `need_review = true` when either:
- top-1 probability is below `prob_threshold` (config, default `0.5`), or
- the margin between top-1 and top-2 probability is below `margin_threshold`
  (config, default `0.1`) — catching cases where the model is confidently
  torn between two classes, not just generally unsure.

`review_reason` records which condition fired: `low_confidence`,
`low_margin`, `both`, or `null`. See `DESIGN_NOTE.md` for the reasoning
behind using both signals.

## Known Limitations (stubbed / out of scope for this exercise)

- **`img_path` is always empty.** Uploaded tiles are processed in memory and
  not persisted to disk. In a real deployment I'd store the raw tile
  (content-hashed filename) to allow re-inference after a model upgrade and
  visual QA when a stored result looks wrong.
- **`review_status` is not wired to a real workflow.** The column exists in
  the schema for a future human-review loop, but there's currently no
  endpoint to transition a flagged row from pending to reviewed. Every row
  is written with a placeholder value.
- **Thresholds are fixed defaults, not empirically derived.** `prob_threshold`
  and `margin_threshold` in `config.yaml` are reasonable starting values, not
  yet validated against the probability distribution of correct vs.
  incorrect predictions on the held-out test set — that analysis is the
  intended next step, not something this exercise implements.
- **Synchronous, single-request processing.** No queue — a burst of
  concurrent tiles is handled one at a time on the request thread. Fine for
  this exercise; would need a local queue/worker for real throughput.
- **No monitoring/alerting, no auth, no multi-node concurrency handling.**
  Explicitly out of scope — see Part 3, Q2 and Q4 for how I'd approach these.

## Part 3 — Problem-Solving Answers

See [`PART3.md`](./PART3.md).
