import cloudinary
import cloudinary.uploader
import cloudinary.api
import django.conf as settings


CLOUDINARY_STORAGE = {
    'CLOUD_NAME': settings.CLOUD_NAME,
    'API_KEY': settings.API_KEY,
    'API_SECRET': settings.API_SECRET, 
}

DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'