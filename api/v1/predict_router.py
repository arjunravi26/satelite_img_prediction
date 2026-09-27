import io
from PIL import Image, UnidentifiedImageError
from fastapi import APIRouter, File, HTTPException, UploadFile, status, Depends
from src.utils.get_service import get_service
from src.service.service import Service
predict_router = APIRouter()

ALLOWED_IMAGE_TYPES = {"image/png"}
REQUIRED_SIZE = (64, 64)


@predict_router.post("/predict")
async def predict(file: UploadFile = File(...), service: Service = Depends(get_service)):

    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Unsupported file type: {file.content_type}. Allowed: {sorted(ALLOWED_IMAGE_TYPES)}",
        )

    try:
        data = await file.read()
        img = Image.open(io.BytesIO(data))
    except (UnidentifiedImageError, OSError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is corrupted or not a readable image.",
        )

    if img.size != REQUIRED_SIZE:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=f"Image size must be {REQUIRED_SIZE[0]}x{REQUIRED_SIZE[1]}, received {img.size[0]}x{img.size[1]}.",
        )

    try:
        prediction = service.predict(img=img,img_name=file.filename)
    except Exception as e:
        print(f"Error is: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Model inference failed.",
        )

    return {"result": f"Result from model: {prediction}"}
