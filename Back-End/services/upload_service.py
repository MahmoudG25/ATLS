import logging
from django.core.files.storage import default_storage
import cloudinary
import cloudinary.uploader
from django.conf import settings

logger = logging.getLogger(__name__)

# Check if Cloudinary is configured
cloudinary_configured = False
try:
    if (getattr(settings, "CLOUDINARY_CLOUD_NAME", None) and
        getattr(settings, "CLOUDINARY_API_KEY", None) and
        getattr(settings, "CLOUDINARY_API_SECRET", None)):
        cloudinary.config(
            cloud_name=settings.CLOUDINARY_CLOUD_NAME,
            api_key=settings.CLOUDINARY_API_KEY,
            api_secret=settings.CLOUDINARY_API_SECRET,
            secure=True,
        )
        cloudinary_configured = True
    else:
        logger.warning("Cloudinary credentials missing, using local storage fallback.")
except Exception as e:
    logger.exception("Error configuring Cloudinary: %s", e)


def upload_file(file_obj, folder="farm-management"):
    if cloudinary_configured:
        try:
            result = cloudinary.uploader.upload(file_obj, folder=folder, resource_type="auto")
            return result["secure_url"]
        except Exception as e:
            logger.error("Cloudinary upload failed, trying local storage: %s", e)

    # Local Storage Fallback
    try:
        # Save file to media/folder/name
        filename = getattr(file_obj, "name", "uploaded_file")
        # Ensure we construct a path relative to the root of the media storage
        file_path = f"{folder}/{filename}"
        saved_path = default_storage.save(file_path, file_obj)

        # Build absolute URL so URLField validates and frontend resolves without getAbsoluteFileUrl
        base_url = getattr(settings, "BACKEND_BASE_URL", "http://localhost:8000").rstrip("/")
        media_url = getattr(settings, "MEDIA_URL", "/media/")
        if not media_url.endswith("/"):
            media_url += "/"
        return f"{base_url}{media_url}{saved_path}"
    except Exception as e:
        logger.exception("Local storage upload failed: %s", e)
        raise e

