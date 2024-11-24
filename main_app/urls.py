from django.urls import path
from .views import *


urlpatterns = [
    path('auth', AuthAPIView.as_view()),
    path('log_out', LogOutAPIView.as_view()),
    path('user', UserAPIView.as_view()),
    path('stats', StatsApiView.as_view()),
    path('categories', CategoryApiView.as_view()),
    path('doctors', DoctorApiView.as_view()),
    path('doctors_search', DoctorSearchApiView.as_view()),
]
