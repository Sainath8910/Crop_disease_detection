from django.urls import path
from . import views

urlpatterns = [
    path('',views.first_view, name='dashboard'),
    path('predict/', views.predict_disease_view, name='predict_disease'),
    path('community/', views.community, name='community'),
    path('post/', views.post, name='post'),
]