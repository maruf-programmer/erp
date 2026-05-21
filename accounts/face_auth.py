import base64
import io

import numpy as np
from PIL import Image, ImageOps


def image_from_data_url(data_url):
    if not data_url or ',' not in data_url:
        raise ValueError('Kamera rasmi topilmadi.')
    _, encoded = data_url.split(',', 1)
    image_bytes = base64.b64decode(encoded)
    return Image.open(io.BytesIO(image_bytes)).convert('RGB')


def image_from_file(file_field):
    file_field.open('rb')
    try:
        return Image.open(file_field).convert('RGB')
    finally:
        file_field.close()


def compare_faces(profile_file, camera_data_url):
    profile_image = image_from_file(profile_file)
    camera_image = image_from_data_url(camera_data_url)

    try:
        return _compare_with_face_recognition(profile_image, camera_image)
    except Exception as e:
        # Only allow demo fallback in DEBUG mode to avoid insecure behaviour in production.
        try:
            from django.conf import settings
            if getattr(settings, 'DEBUG', False):
                is_match, message = _compare_with_demo_similarity(profile_image, camera_image)
                return is_match, f"{message} (demo fallback: {e})"
        except Exception:
            pass
        return False, 'Haqiqiy Face ID uchun face_recognition kutubxonasi ishlamayapti yoki rasmni qayta ishlashda xatolik yuz berdi.'


def _compare_with_face_recognition(profile_image, camera_image):
    import face_recognition

    profile_array = np.array(profile_image)
    camera_array = np.array(camera_image)

    # Detect faces and compute encodings
    profile_locations = face_recognition.face_locations(profile_array)
    camera_locations = face_recognition.face_locations(camera_array)
    profile_encodings = face_recognition.face_encodings(profile_array)
    camera_encodings = face_recognition.face_encodings(camera_array)

    if len(profile_encodings) != 1:
        return False, 'Profil rasmida bitta yuz bo‘lishi kerak. Iltimos profil rasmini tekshiring.'
    if len(camera_encodings) != 1:
        return False, 'Kamerada bitta aniq yuz ko‘rinmadi. Iltimos faqat o‘zingizni ko‘rsating va yorug‘roq joyda qayta urinib ko‘ring.'

    # Use stricter distance threshold for better security
    distance = face_recognition.face_distance([profile_encodings[0]], camera_encodings[0])[0]
    threshold = 0.45
    is_match = distance <= threshold
    return is_match, f'Face ID masofa: {distance:.2f} (threshold {threshold})'


def _compare_with_demo_similarity(profile_image, camera_image):
    profile_hash = _average_hash(profile_image)
    camera_hash = _average_hash(camera_image)
    distance = np.count_nonzero(profile_hash != camera_hash)
    score = 1 - (distance / profile_hash.size)
    is_match = score >= 0.62
    message = f'Demo Face ID o‘xshashlik: {score:.0%}'
    return is_match, message


def _average_hash(image):
    image = ImageOps.fit(image, (160, 160), method=Image.Resampling.LANCZOS)
    image = ImageOps.grayscale(image).resize((16, 16), Image.Resampling.LANCZOS)
    pixels = np.asarray(image, dtype=np.float32)
    return pixels > pixels.mean()
