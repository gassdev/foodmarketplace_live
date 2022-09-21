from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import InMemoryUploadedFile
import os

def allow_only_images_validator(value: InMemoryUploadedFile):
    ext = os.path.splitext(value.name)[1]
    # print(ext)
    valid_extensions = ['.jpg', '.jpeg', '.png']
    if ext.lower() not in valid_extensions:
        raise ValidationError('Unsupported file extension. Allowed extensions: ' +str(valid_extensions))