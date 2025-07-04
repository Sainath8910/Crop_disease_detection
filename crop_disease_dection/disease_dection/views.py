from django.shortcuts import render
import json
from django.conf import settings
import os

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
