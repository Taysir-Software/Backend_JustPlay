from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ActivityViewSet,
    ActivityImageViewSet,
    TimeslotViewSet,
    ReservationViewSet,
    PaymentViewSet,
    CategoryViewSet,
    RegisterView,
    ReviewViewSet, 
    CancellationLogViewSet, 
    ExploitantProfileViewSet
)

router = DefaultRouter()
router.register(r'activites', ActivityViewSet)
router.register(r'images-activites', ActivityImageViewSet)
router.register(r'creneaux', TimeslotViewSet, basename='creneaux')
router.register(r'reservations', ReservationViewSet, basename='reservations')
router.register(r'paiements', PaymentViewSet, basename='paiements')
router.register(r'categories', CategoryViewSet, basename='categories')
router.register(r'reviews', ReviewViewSet, basename='reviews')
router.register(r'annulations', CancellationLogViewSet, basename='annulations')
router.register(r'exploitants-profil', ExploitantProfileViewSet, basename='exploitant-profile')

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('', include(router.urls)),
]
