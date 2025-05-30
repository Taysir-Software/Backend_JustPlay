from rest_framework import serializers
from .models import User, Activity, ActivityImage, Timeslot, Reservation, Payment, Category, ExploitantProfile , Review, CancellationLog
from django.contrib.auth.password_validation import validate_password


# --------------------------
# USER (sans champ "role" exposé)
# --------------------------
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'date_joined']
        read_only_fields = ['id', 'date_joined']

# --------------------------
# PROFIL EXPLOITANT (sans champ "user" exposé)
# --------------------------

class ExploitantProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExploitantProfile
        fields = [
            'company_name',
            'logo',
            'website',
            'contact_phone',
            'description',
        ]


# --------------------------
# CATÉGORIE
# --------------------------
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']


# --------------------------
# ACTIVITÉ IMAGE (Nested)
# --------------------------
class ActivityImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityImage
        fields = ['id', 'image', 'uploaded_at']


# --------------------------
# ACTIVITÉ
# --------------------------
class ActivitySerializer(serializers.ModelSerializer):
    images = ActivityImageSerializer(many=True, read_only=True)
    categories = CategorySerializer(many=True, read_only=True)  # nested en lecture
    category_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Category.objects.all(),
        write_only=True,
        source='categories'
    )

    class Meta:
        model = Activity
        fields = [
            'id', 'name', 'description', 'exploitant', 'exploitant_user',
            'is_active', 'price', 'average_rating',
            'created_at', 'updated_at',
            'images', 'categories', 'category_ids'
        ]
        read_only_fields = ['created_at', 'updated_at', 'exploitant_user', 'average_rating']


# --------------------------
# CRÉNEAU HORAIRE
# --------------------------
class TimeslotSerializer(serializers.ModelSerializer):
    activity = ActivitySerializer(read_only=True)

    class Meta:
        model = Timeslot
        fields = ['id', 'activity', 'start_time', 'end_time', 'is_booked']


# --------------------------
# RÉSERVATION
# --------------------------
class ReservationSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    timeslot = TimeslotSerializer(read_only=True)

    class Meta:
        model = Reservation
        fields = ['id', 'user', 'timeslot', 'reservation_date', 'status']


# --------------------------
# PAIEMENT
# --------------------------
class PaymentSerializer(serializers.ModelSerializer):
    reservation = ReservationSerializer(read_only=True)

    class Meta:
        model = Payment
        fields = ['id', 'reservation', 'amount', 'method', 'status', 'payment_date']

# --------------------------
# USER CRÉATION (pour l'inscription)
# --------------------------
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password'],
            role='client'  # ← sécurité : ne jamais accepter depuis l'extérieur
        )
        return user

# --------------------------
# REVIEW
# --------------------------

class ReviewSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    activity = serializers.StringRelatedField(read_only=True)
    
    class Meta:
        model = Review
        fields = ['id', 'user', 'activity', 'rating', 'comment', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']


# --------------------------
# LOG D'ANNULATION
# --------------------------

class CancellationLogSerializer(serializers.ModelSerializer):
    cancelled_by = serializers.StringRelatedField(read_only=True)
    reservation = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = CancellationLog
        fields = ['id', 'reservation', 'cancelled_by', 'reason', 'cancelled_at']
        read_only_fields = ['id', 'cancelled_by', 'cancelled_at', 'reservation']