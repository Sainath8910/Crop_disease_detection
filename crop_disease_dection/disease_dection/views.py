from django.shortcuts import render
from django.conf import settings
from django.core.files.storage import default_storage
import os
import json
import numpy as np
from tensorflow.keras.models import load_model
from PIL import Image

# ------------------- Load Model and Labels Once -------------------

MODEL_PATH = os.path.join(settings.BASE_DIR, 'disease_dection', 'models', 'crop_disease_model.h5')
model = load_model(MODEL_PATH)

LABELS_PATH = os.path.join(settings.BASE_DIR, 'disease_dection', 'models', 'class_indices.json')
with open(LABELS_PATH, 'r') as f:
    class_indices = json.load(f)
    label_map = {v: k for k, v in class_indices.items()}


# ------------------- Dashboard View -------------------

def first_view(request):
    """
    Loads crop names from a JSON file and renders the dashboard.
    """
    try:
        file_path = os.path.join(settings.BASE_DIR, 'disease_dection', 'data.json')
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        crop_list = list(data.keys())
    except (FileNotFoundError, json.JSONDecodeError) as e:
        crop_list = []
        print(f"Error loading JSON: {e}")

    return render(request, 'disease_dection/dashboard.html', {'crop_list': crop_list})


# ------------------- Prediction View -------------------

def predict_disease_view(request):
    """
    Handles image upload, runs prediction using the ML model,
    and displays crop disease information.
    """
    if request.method == 'POST' and request.FILES.get('image') and request.POST.get('crop'):
        img_file = request.FILES['image']
        crop_type = request.POST.get('crop')

        try:
            # Load and preprocess the image
            img = Image.open(img_file).convert('RGB')
            img = img.resize((128, 128))  # Must match model input size
            img_array = np.array(img) / 255.0
            img_array = np.expand_dims(img_array, axis=0)

            # Make prediction
            prediction = model.predict(img_array)
            predicted_class_index = np.argmax(prediction)
            predicted_label = label_map[predicted_class_index]

            # Extract crop and disease
            try:
                predicted_crop, predicted_disease = predicted_label.split('_', 1)
            except ValueError:
                predicted_crop = crop_type
                predicted_disease = predicted_label

            # Load disease info from JSON
            json_path = os.path.join(settings.BASE_DIR, 'disease_dection', 'data.json')
            with open(json_path, 'r', encoding='utf-8') as f:
                disease_data = json.load(f)

            disease_info = disease_data.get(predicted_crop, {}).get(predicted_disease, {})

            # Save uploaded image temporarily
            saved_path = default_storage.save('temp_uploaded_image.jpg', img_file)
            image_url = default_storage.url(saved_path)

            return render(request, 'disease_dection/result.html', {
                'predicted_crop': predicted_crop,
                'predicted_disease': disease_info.get('name', 'N/A'),
                'reason': disease_info.get('reason', 'N/A'),
                'description': disease_info.get('description', 'N/A'),
                'suggestion': disease_info.get('suggestion', 'N/A'),
                'image_url': image_url,
            })

        except Exception as e:
            return render(request, 'disease_dection/dashboard.html', {
                'error': f"Prediction failed: {str(e)}"
            })

    # If form is incomplete
    return render(request, 'disease_dection/dashboard.html', {
        'error': 'Please upload an image and select a crop.'
    })