import cloudinary
import cloudinary.uploader
from django.conf import settings


cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET,
    secure=True,
)


def upload_file(file_obj, folder="farm-management"):
    result = cloudinary.uploader.upload(file_obj, folder=folder, resource_type="auto")
    return result["secure_url"]
