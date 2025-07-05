from rest_framework import viewsets, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from django.utils import timezone
from .models import Activity, ActivityImage, Timeslot, Reservation, Payment , Category, Review, CancellationLog, ExploitantProfile, Membership, APIKey
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
    ExploitantProfileSerializer,
    MembershipSerializer,
    ExternalReservationWebhookSerializer
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

# -------------------------
# ADHÉSIONS (par rôle)
# -------------------------
class MembershipViewSet(viewsets.ModelViewSet):
    queryset = Membership.objects.all()
    serializer_class = MembershipSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return Membership.objects.all()
        return Membership.objects.filter(user=user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


# ------------------------- 
# CLÉ API (admin seulement)
# -------------------------

class WebhookReservationView(APIView):
    permission_classes = []  # Pas d'authentification JWT ici

    def post(self, request):
        api_key = request.headers.get("X-API-KEY")
        if not api_key:
            raise PermissionDenied("Clé API manquante.")

        try:
            key_obj = APIKey.objects.select_related("user").get(key=api_key)
            if key_obj.is_expired():
                raise PermissionDenied("Clé API expirée.")
        except APIKey.DoesNotExist:
            raise PermissionDenied("Clé API invalide.")

        serializer = ExternalReservationWebhookSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data

        # Vérifie que l'exploitant_id correspond bien à la clé
        if data["exploitant_id"] != key_obj.user.id:
            raise PermissionDenied("ID utilisateur incorrect pour cette clé API.")

        # Vérifie que l'activité existe et appartient à cet exploitant
        try:
            activity = Activity.objects.get(id=data["activity_id"], exploitant_user=key_obj.user)
        except Activity.DoesNotExist:
            return Response({"detail": "Activité introuvable ou non autorisée."}, status=404)

        # Crée un créneau si inexistant (même date/heure pour cette activité)
        timeslot, created = Timeslot.objects.get_or_create(
            activity=activity,
            start_time=data["start_time"],
            end_time=data["end_time"],
            defaults={"is_booked": True}
        )
        if not created and timeslot.is_booked:
            return Response({"detail": "Ce créneau est déjà réservé."}, status=400)

        timeslot.is_booked = True
        timeslot.save()

        # Crée une réservation liée à cet exploitant
        Reservation.objects.create(
            user=key_obj.user,
            timeslot=timeslot,
            status="paid",
            source="exploitant"
        )

        return Response({"message": "Réservation reçue avec succès."}, status=201)
