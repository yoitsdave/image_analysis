import os
from .forms import ImageForm, ImageSegmentationForm
from .models import Image, ImageSegmentation
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

# import numpy as np
# from tensorflow.keras.applications.resnet50 import ResNet50
# from tensorflow.keras.preprocessing import image
# from tensorflow.keras.applications.resnet50 import preprocess_input, decode_predictions

import torch
from torchvision import transforms
from PIL import Image as PILImage
import numpy as np

@login_required
def home(request):
    user = request.user
    all_images = Image.objects.filter(owner=user).filter(active=True)

    num_images = len(all_images)
    if num_images == 0:
        images_msg = "No images uploaded - upload more to continue!"
        images_link_text = "upload an image"

        classifier_msg = "Upload images before you can see the classifier!"
        classifier_link_text = ""

    else:
        images_msg = str(num_images) + " image(s) uploaded - proceed to further steps if ready, or"
        images_link_text = "upload another image"

        classifier_msg = "score how well the classifier labels the images - "
        classifier_link_text = "rate classifier labels"


    all_default_segments = ImageSegmentation.objects.filter(owner=user).filter(noisy=False).values_list("image_id", flat=True)
    all_noisy_segments = ImageSegmentation.objects.filter(owner=user).filter(noisy=True).values_list("image_id", flat=True)
    unlabeled_default = all_images.exclude(id__in=all_default_segments).values_list("id", flat=True)
    unlabeled_noisy = all_images.exclude(id__in=all_noisy_segments).values_list("id", flat=True)

    if not all_images.exists():
        segment_msg = "Upload images before you can segment anything!"
        segment_link = ""
        segment_link_text = ""
    elif unlabeled_default.exists():
        segment_msg = "Next"
        segment_link = "segment/default/" + str(unlabeled_default.first()) + "/"
        segment_link_text = "segment next image"
    elif unlabeled_noisy.exists():
        segment_msg = "Next"
        segment_link = "segment/noisy/" + str(unlabeled_noisy.first()) + "/"
        segment_link_text = "segment next image (noisy)"
    else:
        segment_msg = "All images segmented!"
        segment_link = ""
        segment_link_text = ""

    return render(request, 'home.html', context={
        'user': user, 
        "images_msg": images_msg, 
        "images_link_text": images_link_text,
        "segment_msg": segment_msg,
        "segment_link": segment_link,
        "segment_link_text": segment_link_text,
        "classifier_msg": classifier_msg,
        "classifier_link_text": classifier_link_text,
    })

@login_required
def upload(request):
 
    if request.method == 'POST':
        form = ImageForm(request.POST, request.FILES)
 
        if form.is_valid():
            candidate = form.save(commit=False)
            candidate.owner = request.user
            candidate.save()
            return redirect('/')
    else:
        form = ImageForm()

    return render(request, 'upload.html', {'form': form})
 

def segment_get_path_label_form(request, id):
    #TODO: check to see if image is owned by user - otherwise dont send page

    image = Image.objects.filter(id=id).first()
    path = image.img.url
    label = image.label

    if request.method == 'POST':
        form = ImageSegmentationForm(request.POST, request.FILES)
 
        if form.is_valid():
            candidate = form.save(commit=False)
            candidate.owner = request.user
            candidate.image = image
            candidate.save()
            return 0, 0, 0, True
    else:
        form = ImageSegmentationForm()

    return path, label, form, False


@login_required
def segment_default(request, id):
    path, label, form, form_submitted = segment_get_path_label_form(request, id)

    if form_submitted:
        return redirect('/')  #TODO: redirect to the next image to segment instead of home maybe?
    else:
        return render(request, 'segment_default.html', {"image_url": path, "label": label, "form": form})

@login_required
def segment_noisy(request, id):
    path, label, form, form_submitted = segment_get_path_label_form(request, id)

    if form_submitted:
        return redirect('/')
    else:
        return render(request, 'segment_noisy.html', {"image_url": path, "label": label, "form": form})


def prepare_image(path):
    img_transforms = transforms.Compose(
        [transforms.Resize(256), transforms.CenterCrop(224), transforms.ToTensor()]
    )

    img = PILImage.open(path)
    if img.mode != "RGB":
        img = img.convert("RGB")


    img = img_transforms(img)
    with torch.no_grad():
        # mean and std are not multiplied by 255 as they are in training script
        # torch dataloader reads data into bytes whereas loading directly
        # through PIL creates a tensor with floats in [0,1] range
        mean = torch.tensor([0.485, 0.456, 0.406]).view(1, 3, 1, 1)
        std = torch.tensor([0.229, 0.224, 0.225]).view(1, 3, 1, 1)
        img = img.float()
        input = img.unsqueeze(0).sub_(mean).div_(std)

    return input


@login_required
def score_classifier(request):
    user = request.user
    all_images = Image.objects.filter(owner=user).filter(active=True)
    # image_urls = [os.path.join("/", "static", "images", os.path.basename(image.img.path)) for image in all_images]
    image_urls = [image.img.url for image in all_images]

    device = torch.device("cpu")
    resnet50 = torch.hub.load('NVIDIA/DeepLearningExamples:torchhub', 'nvidia_resnet50', pretrained=True)
    utils = torch.hub.load('NVIDIA/DeepLearningExamples:torchhub', 'nvidia_convnets_processing_utils')
    resnet50.eval().to(device)

    img_transforms = transforms.Compose(
        [transforms.Resize(256), transforms.CenterCrop(224), transforms.ToTensor()]
    )

    batch = torch.cat(
        [prepare_image(image.img.path) for image in all_images]
    ).to(device)

    with torch.no_grad():
        output = torch.nn.functional.softmax(resnet50(batch), dim=1)

    results = utils.pick_n_best(predictions=output, n=1)
    labels = []
    for i, uploaded_image in enumerate(all_images):
        labels.append(results[i][0][0])

    indices = range(len(labels))
    image_data = zip(indices, labels, image_urls)

    return render(request, 'score.html', {"image_data": image_data})
