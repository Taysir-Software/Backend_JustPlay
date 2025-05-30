from rest_framework import viewsets, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from .models import Activity, ActivityImage, Timeslot, Reservation, Payment , Category, Review, CancellationLog, ExploitantProfile
from .serializers import (
    ActivitySerializer,
    ActivityImageSerializer,
    TimeslotSerializer,
    ReservationSerializer,
    PaymentSerializer,
    CategorySerializer,
    RegisterSerializer,
    ReviewSerializer,
    CancellationLogSerializer, 
    ExploitantProfileSerializer
)
from .permissions import (
    IsAdminUser,
    IsAdminOrReadOnly,
    IsOwner,
    IsExploitantUser,
    IsAdminOrExploitant
)


# -------------------------
# ACTIVITÉS (par rôle)
# -------------------------
class ActivityViewSet(viewsets.ModelViewSet):
    queryset = Activity.objects.all()
    serializer_class = ActivitySerializer
    permission_classes = [IsAdminOrExploitant]

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            if user.role == 'admin':
                return Activity.objects.all()
            elif user.role == 'exploitant':
                return Activity.objects.filter(exploitant_user=user)
        return Activity.objects.filter(is_active=True)  # clients ou anonymes

    def perform_create(self, serializer):
        user = self.request.user
        if user.role == 'exploitant':
            serializer.save(exploitant_user=user)
        elif user.role == 'admin':
            serializer.save()
        else:
            raise permissions.PermissionDenied("Seuls les admins ou exploitants peuvent créer une activité.")

    def perform_update(self, serializer):
        user = self.request.user
        instance = self.get_object()
        if user.role == 'exploitant' and instance.exploitant_user != user:
            raise permissions.PermissionDenied("Vous ne pouvez modifier que vos propres activités.")
        serializer.save()


# -------------------------
# IMAGES D’ACTIVITÉS (admin seulement)
# -------------------------
class ActivityImageViewSet(viewsets.ModelViewSet):
    queryset = ActivityImage.objects.all()
    serializer_class = ActivityImageSerializer
    permission_classes = [IsAdminUser]


# -------------------------
# CRÉNEAUX DISPONIBLES (public)
# -------------------------
class TimeslotViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = TimeslotSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return Timeslot.objects.filter(is_booked=False)


# -------------------------
# RÉSERVATIONS (par rôle)
# -------------------------
class ReservationViewSet(viewsets.ModelViewSet):
    serializer_class = ReservationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return Reservation.objects.all()
        elif user.role == 'exploitant':
            return Reservation.objects.filter(timeslot__activity__exploitant_user=user)
        return Reservation.objects.filter(user=user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


# -------------------------
# PAIEMENTS (par rôle)
# -------------------------
class PaymentViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return Payment.objects.all()
        elif user.role == 'exploitant':
            return Payment.objects.filter(reservation__timeslot__activity__exploitant_user=user)
        return Payment.objects.filter(reservation__user=user)

# -------------------------
# CATÉGORIES (admin seulement)
# -------------------------
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminUser]

    def perform_create(self, serializer):
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()

# class CategoryViewSet(viewsets.ReadOnlyModelViewSet):  # ou ModelViewSet si admin les gère
#     queryset = Category.objects.all()
#     serializer_class = CategorySerializer
#     permission_classes = [permissions.AllowAny]  # ou [IsAdminUser] si restreint

# -------------------------
# INSCRIPTION (public)
# -------------------------
class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({'message': 'Compte créé avec succès.'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# -------------------------
# AVIS ET COMMENTAIRES (par rôle)
# -------------------------

class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Review.objects.all()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

# -------------------------
# LOGS D'ANNULATION (admin seulement)
# -------------------------

class CancellationLogViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CancellationLogSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        return CancellationLog.objects.all()

# -------------------------
# PROFIL EXPLOITANT (par rôle)
# -------------------------

class ExploitantProfileViewSet(viewsets.ModelViewSet):
    serializer_class = ExploitantProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return ExploitantProfile.objects.all()
        elif user.role == 'exploitant':
            return ExploitantProfile.objects.filter(user=user)
        raise PermissionDenied("Accès réservé aux exploitants ou admins.")

    def perform_update(self, serializer):
        if self.request.user.role != 'exploitant':
            raise PermissionDenied("Seul l’exploitant peut modifier son profil.")
        serializer.save(user=self.request.user)