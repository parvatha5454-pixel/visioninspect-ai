from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, auth
from ..database import get_db
from ..vision import detector, preprocessing

router = APIRouter(prefix="/inspections", tags=["Inspections"])


@router.post("/run/{image_id}")
def run_inspection(
    image_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    image = db.query(models.Image).filter(models.Image.image_id == image_id).first()
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")

    category = (
        db.query(models.Category)
        .filter(models.Category.category_id == image.category_id)
        .first()
    )
    if not category:
        raise HTTPException(status_code=400, detail="Image has no category")

    if not detector.has_reference(category.category_name):
        raise HTTPException(
            status_code=400,
            detail=(
                f"No trained reference for category '{category.category_name}'. "
                f"Run build_references.py on the backend first."
            ),
        )

    try:
        prediction = detector.predict(image.image_path, category.category_name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Inspection failed: {e}")

    # quality report is informational only, not persisted in this milestone
    raw_img = preprocessing.load_image(image.image_path)
    quality = preprocessing.quality_report(raw_img)

    inspection = models.Inspection(
        image_id=image.image_id,
        inspected_by=current_user.user_id,
        status="completed",
        result=prediction["result"],
        confidence_score=prediction["anomaly_score"],
    )
    db.add(inspection)
    db.commit()
    db.refresh(inspection)

    if prediction["result"] == "defective":
        defect = models.Defect(
            inspection_id=inspection.inspection_id,
            defect_type="anomaly",
            severity=prediction["severity"],
            location_data=None,
        )
        db.add(defect)
        db.commit()

    return {
        "inspection_id": inspection.inspection_id,
        "result": prediction["result"],
        "anomaly_score": prediction["anomaly_score"],
        "severity": prediction["severity"],
        "quality": quality,
    }
