from django import forms
from .models import Image, ImageSegmentation
 
 
class ImageForm(forms.ModelForm):
 
    class Meta:
        model = Image
        fields = ["label", "img"]
        exclude = ["owner"]

class ImageSegmentationForm(forms.ModelForm):

    class Meta:
        model = ImageSegmentation
        fields = ["data", "noisy"]
        exclude = ["image", "owner"]
