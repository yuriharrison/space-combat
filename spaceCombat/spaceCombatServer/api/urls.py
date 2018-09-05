from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
# router.register('room', )

urlpatterns = [
    path('create_room/', views.create_room),
    path('join_room/', views.join_room),
    path('disconnect/<str:hash>/', views.disconnect),
    path('players/<int:room_code>/', views.GetPlayers.as_view()),
]