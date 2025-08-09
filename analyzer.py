# src/analyzer.py
from deepface import DeepFace

def get_face_attributes(face_image):
    """Analyzes a face image to get gender and age."""
    try:
        analysis = DeepFace.analyze(
            img_path=face_image,
            actions=['age', 'gender'],
            enforce_detection=False,
            silent=True
        )
        result = analysis[0]
        return {
            "gender": result.get('dominant_gender', 'person'),
            "age": result.get('age', 30)
        }
    except Exception:
        return None # Return None if analysis fails