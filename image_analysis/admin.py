from django.contrib import admin
from .models import Image, ImageSegmentation

admin.site.register(Image)
admin.site.register(ImageSegmentation)