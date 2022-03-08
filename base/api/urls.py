from django.urls import path
from . import views

urlpatterns = [
    path('', views.getRoutes),
    path('rooms/', views.getRooms),
    path('room/<str:pk>', views.getRoom),

    path('messages/', views.getMessages),
    path('messages/<str:pk>', views.getMessagesByUser),
]