import os
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.auth import get_current_user
from app.models.user import User
from app.config import settings
from app.utils.face_utils import compare_faces

router = APIRouter(prefix="/api/kyc", tags=["kyc"])


@router.post("/enroll")
async def enroll_kyc(
    id_card: UploadFile = File(...),
    selfie: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Recibe la foto de la cédula (subida por el usuario) y una selfie en vivo
    capturada por la webcam.
    Compara ambos rostros con IA. Si la similitud es suficiente, registra al
    usuario como verificado KYC y guarda su selfie como baseline biométrico.
    """
    # Guardar las imágenes en el directorio del usuario
    user_kyc_dir = os.path.join(settings.upload_dir, "kyc_profiles", str(current_user.id))
    os.makedirs(user_kyc_dir, exist_ok=True)

    id_path = os.path.join(user_kyc_dir, "id_card.jpg")
    selfie_path = os.path.join(user_kyc_dir, "selfie_baseline.jpg")

    with open(id_path, "wb") as f:
        f.write(await id_card.read())
    with open(selfie_path, "wb") as f:
        f.write(await selfie.read())

    try:
        result = compare_faces(id_path, selfie_path)
    except (ValueError, IOError) as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error interno durante la verificación biométrica: {str(e)}"
        )

    if result["verified"]:
        current_user.is_kyc_verified = True
        current_user.kyc_baseline_path = selfie_path
        db.commit()
        return {
            "verified": True,
            "similarity": result["similarity"],
            "message": (
                f"✅ Identidad validada con éxito. "
                f"Similitud facial: {result['similarity']}%"
            ),
        }
    else:
        return {
            "verified": False,
            "similarity": result["similarity"],
            "message": (
                f"❌ Los rostros no coinciden suficientemente. "
                f"Similitud obtenida: {result['similarity']}% "
                f"(mínimo requerido: 70%). "
                f"Asegúrate de que la foto de la cédula sea clara y tómate la selfie con buena luz."
            ),
        }
