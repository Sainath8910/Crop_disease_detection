from django.shortcuts import render
import json
from django.conf import settings
import os

def first_view(request):
    """
    Redirects to the dashboard view.
    """
    file_path = os.path.join(settings.BASE_DIR, 'disease_dection', 'data.json')
    with open(file_path, 'r') as f:
        crop_list = json.load(f)
    return render(request,'disease_dection/dashboard.html',{'crop_list':crop_list})
