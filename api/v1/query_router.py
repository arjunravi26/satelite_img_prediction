from fastapi import APIRouter, HTTPException, Query, Request, Depends
from typing import Optional
from src.db.prediction_db import DB

query_router = APIRouter()
db = DB()

@query_router.get("/result")
async def query_predictions(request: Request,
    predicted_cls: Optional[str] = Query(default=None),
    min_confidence: Optional[float] = Query(
        default=None,
        ge=0.0,
        le=1.0
    ),
    max_confidence: Optional[float] = Query(
        default=None,
        ge=0.0,
        le=1.0
    ),
    need_review: Optional[bool] = Query(default=None),
    review_status: Optional[str] = Query(default=None),
    model_version: Optional[str] = Query(default=None),
    limit: int = Query(default=100, ge=1, le=1000),
):
    try:
        if (
            min_confidence is not None
            and max_confidence is not None
            and min_confidence > max_confidence
        ):
            raise HTTPException(
                status_code=400,
                detail="min_confidence cannot be greater than max_confidence"
            )

        results = db.search_predictions(
            predicted_cls=predicted_cls,
            min_confidence=min_confidence,
            max_confidence=max_confidence,
            need_review=need_review,
            review_status=review_status,
            model_version=model_version,
            limit=limit,
        )

        return {
            "count": len(results),
            "results": results
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to query predictions: {str(e)}"
        )