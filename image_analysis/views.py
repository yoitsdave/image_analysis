import os
from .forms import ImageForm, ImageSegmentationForm
from .models import Image, ImageSegmentation

# import numpy as np
# from django.shortcuts import render, redirect
# from django.contrib.auth.decorators import login_required
# from tensorflow.keras.applications.resnet50 import ResNet50
# from tensorflow.keras.preprocessing import image
# from tensorflow.keras.applications.resnet50 import preprocess_input, decode_predictions


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
    path = os.path.join("/", "images", os.path.basename(image.img.path))
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
    
@login_required
def score_classifier(request):
    user = request.user
    all_images = Image.objects.filter(owner=user).filter(active=True)
    image_urls = [os.path.join("/", "images", os.path.basename(image.img.path)) for image in all_images]


    # model = ResNet50(weights='imagenet')
    labels = []
    for uploaded_image in all_images:
        # img = image.load_img(uploaded_image.img.path, target_size=(224, 224))
        # x = image.img_to_array(img)
        # x = np.expand_dims(x, axis=0)
        # x = preprocess_input(x)
        # preds = model.predict(x)
        # label = decode_predictions(preds, top=1)[0][0][1]

        label = "sample_label"

        labels.append(label)


    indices = range(len(labels))
    image_data = zip(indices, labels, image_urls)

    return render(request, 'score.html', {"image_data": image_data})
