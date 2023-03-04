from django.db import models
from django.contrib.auth.models import User

class Image(models.Model):
    label = models.CharField(max_length=255)
    created_on = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    active = models.BooleanField(default=True)
    img = models.ImageField(upload_to='static/images/')

class ImageSegmentation(models.Model):
    image = models.ForeignKey(Image, on_delete=models.CASCADE)
    created_on = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    data = models.FileField(upload_to='static/seg/')
    noisy = models.BooleanField()