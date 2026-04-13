"""
Módulo de comparación facial basado en OpenCV + NumPy.
Optimizado para cédulas de identidad ecuatorianas, donde la foto principal
del titular se ubica en la zona inferior-izquierda del documento.
"""
import cv2
import numpy as np

# Clasificador Haar Cascade incluido en OpenCV (sin descargas adicionales)
_FACE_CASCADE = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

# Umbral de similitud coseno: ≥ 0.70 = misma persona (70%)
SIMILARITY_THRESHOLD = 0.70


def _detect_largest_face(img_bgr: np.ndarray, min_face_px: int = 20) -> np.ndarray | None:
    """
    Detecta el rostro más grande en la imagen completa.
    Prueba múltiples escalas de detección.
    Retorna la ROI del rostro en escala de grises o None.
    """
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    best_face = None
    best_area = 0

    for scale_factor in [1.05, 1.1, 1.15, 1.2, 1.3]:
        faces = _FACE_CASCADE.detectMultiScale(
            gray,
            scaleFactor=scale_factor,
            minNeighbors=4,
            minSize=(min_face_px, min_face_px),
        )
        for (x, y, w, h) in faces:
            area = w * h
            if area > best_area:
                best_area = area
                best_face = (x, y, w, h)

    if best_face is None:
        return None

    x, y, w, h = best_face
    pad = int(0.12 * min(w, h))
    x1 = max(0, x - pad)
    y1 = max(0, y - pad)
    x2 = min(gray.shape[1], x + w + pad)
    y2 = min(gray.shape[0], y + h + pad)
    return gray[y1:y2, x1:x2]


def _detect_face_in_id_card(img_bgr: np.ndarray) -> np.ndarray | None:
    """
    Detecta el rostro en una cédula de identidad ecuatoriana.

    En la cédula ecuatoriana, la foto principal del titular ocupa
    la zona IZQUIERDA del documento (aprox. el 35% izquierdo).
    También se intenta en toda la imagen como fallback.
    """
    h, w = img_bgr.shape[:2]

    # Estrategia 1: buscar en la mitad izquierda (donde está la foto en la cédula)
    left_half = img_bgr[:, : int(w * 0.40)]
    face = _detect_largest_face(left_half, min_face_px=15)
    if face is not None:
        return face

    # Estrategia 2: buscar en toda la imagen (por si la foto fue recortada o girada)
    face = _detect_largest_face(img_bgr, min_face_px=15)
    if face is not None:
        return face

    # Estrategia 3: zona inferior-izquierda (cédulas más antiguas)
    bottom_left = img_bgr[int(h * 0.4) :, : int(w * 0.45)]
    return _detect_largest_face(bottom_left, min_face_px=10)


def _face_to_embedding(face_gray: np.ndarray) -> np.ndarray:
    """
    Convierte un ROI de rostro en un vector de características normalizado.
    Aplica CLAHE para igualar diferencias de iluminación entre
    fotos de cédula (baja calidad) y selfies (alta calidad / webcam).
    """
    face_resized = cv2.resize(face_gray, (128, 128))

    # Contrast Limited Adaptive Histogram Equalization:
    # normaliza la iluminación sin amplificar el ruido
    clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
    normalized = clahe.apply(face_resized)

    # Vector de descriptores L2-normalizado
    vec = normalized.flatten().astype(np.float64)
    norm = np.linalg.norm(vec)
    return vec / norm if norm > 0 else vec


def compare_faces(id_card_path: str, selfie_path: str) -> dict:
    """
    Compara el rostro de una cédula ecuatoriana con una selfie.

    Args:
        id_card_path: Ruta a la imagen de la cédula de identidad.
        selfie_path:  Ruta a la selfie tomada por webcam.

    Returns:
        dict con:
          - verified (bool): True si las caras coinciden.
          - similarity (float): Porcentaje de similitud (0-100).
          - distance (float): Distancia coseno (0=idénticos, 1=diferentes).

    Raises:
        ValueError: Si no se detecta rostro en alguna imagen.
        IOError: Si no se puede leer alguna imagen.
    """
    img_cedula = cv2.imread(id_card_path)
    img_selfie = cv2.imread(selfie_path)

    if img_cedula is None:
        raise IOError("No se pudo leer la foto de la cédula.")
    if img_selfie is None:
        raise IOError("No se pudo leer la selfie.")

    # Usar la detección especializada para cédula ecuatoriana
    face_cedula = _detect_face_in_id_card(img_cedula)
    # Para la selfie, buscar en toda la imagen
    face_selfie = _detect_largest_face(img_selfie, min_face_px=40)

    if face_cedula is None:
        raise ValueError(
            "No se detectó ningún rostro en la foto de la cédula. "
            "Asegúrate de que la imagen esté bien iluminada, "
            "sin reflejos y que el lado izquierdo de la cédula sea completamente visible."
        )
    if face_selfie is None:
        raise ValueError(
            "No se detectó ningún rostro en tu selfie. "
            "Mira directamente a la cámara, asegúrate de tener "
            "buena iluminación frontal y que tu rostro ocupe el centro."
        )

    emb_cedula = _face_to_embedding(face_cedula)
    emb_selfie = _face_to_embedding(face_selfie)

    # Similitud coseno (dot product de vectores L2-normalizados)
    similarity = float(np.clip(np.dot(emb_cedula, emb_selfie), 0.0, 1.0))
    verified = similarity >= SIMILARITY_THRESHOLD

    return {
        "verified": verified,
        "similarity": round(similarity * 100, 1),
        "distance": round(1.0 - similarity, 4),
    }
