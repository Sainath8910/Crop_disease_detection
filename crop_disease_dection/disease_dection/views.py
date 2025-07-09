from django.shortcuts import render
import json
from django.conf import settings
import os
from tensorflow.keras.models import load_model

# Load the ML model (once per server restart)
MODEL_PATH = os.path.join(settings.BASE_DIR, 'disease_dection', 'models', 'crop_disease_model.h5')
model = load_model(MODEL_PATH)

# Load class label mapping
LABELS_PATH = os.path.join(settings.BASE_DIR, 'disease_dection', 'models', 'class_indices.json')
with open(LABELS_PATH, 'r') as f:
    class_indices = json.load(f)
    label_map = {v: k for k, v in class_indices.items()}


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

def predict_disease_view(request):
    if request.method == 'POST' and request.FILES.get('image') and request.POST.get('crop'):
        img_file = request.FILES['image']
        crop_type = request.POST.get('crop')

        # Save to temp
        from PIL import Image
        from io import BytesIO

        img = Image.open(img_file).convert('RGB')
        img = img.resize((128, 128))  # Same as model input
        img_array = np.array(img) / 255.0
        img_array = np.expand_dims(img_array, axis=0)

        prediction = model.predict(img_array)
        predicted_class_index = np.argmax(prediction)
        predicted_label = label_map[predicted_class_index]

        # Load disease descriptions
        with open(os.path.join(settings.BASE_DIR, 'disease_dection', 'data.json'), 'r', encoding='utf-8') as f:
            disease_data = json.load(f)

        # Extract disease name and details
        predicted_crop, predicted_disease = predicted_label.split('_', 1)
        disease_info = disease_data.get(predicted_crop, {}).get(predicted_disease, {})

        return render(request, 'disease_dection/result.html', {
            'predicted_crop': predicted_crop,
            'predicted_disease': predicted_disease,
            'reason': disease_info.get('reason', 'N/A'),
            'description': disease_info.get('description', 'N/A'),
            'suggestion': disease_info.get('suggestion', 'N/A'),
        })

    return render(request, 'disease_dection/dashboard.html', {'error': 'Please upload an image and select a crop.'})


