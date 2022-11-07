from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='user-home'),
    path('history', views.history, name='user-history'),
    path('history_detail/<int:pk>',
         views.history_detail, name='history_detail'),
]

