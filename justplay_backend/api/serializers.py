
from rest_framework import serializers
from .models import (
    User, Activity, ActivityImage, Timeslot, Reservation, Payment,
    Category, ExploitantProfile, Review, CancellationLog, Membership
)
from django.contrib.auth.password_validation import validate_password

# --------------------------
# USER (avec champ is_member)
# --------------------------
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'date_joined', 'is_member']
        read_only_fields = ['id', 'date_joined', 'is_member']

# --------------------------
# PROFIL EXPLOITANT
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
    categories = CategorySerializer(many=True, read_only=True)
    category_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Category.objects.all(),
        write_only=True,
        source='categories'
    )
    final_price = serializers.SerializerMethodField()

    class Meta:
        model = Activity
        fields = [
            'id', 'name', 'description', 'exploitant', 'exploitant_user',
            'is_active', 'price', 'average_rating',
            'created_at', 'updated_at',
            'images', 'categories', 'category_ids',
            'member_price', 'final_price',
            'is_reservable', 'contact_name', 'contact_email', 'contact_phone', 'external_form_url'
        ]
        read_only_fields = ['created_at', 'updated_at', 'exploitant_user', 'average_rating']

    def get_final_price(self, obj):
        user = self.context['request'].user
        if user.is_authenticated and getattr(user, 'is_member', False) and obj.member_price:
            return obj.member_price
        return obj.price
    
    def validate(self, data):
        if data.get('is_reservable') is False:
            if not data.get('contact_email') and not data.get('contact_phone') and not data.get('external_form_url'):
                raise serializers.ValidationError("Un moyen de contact doit être fourni si l'activité n'est pas réservable.")
        return data

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
        fields = ['id', 'user', 'timeslot', 'reservation_date', 'status', 'source']

# --------------------------
# PAIEMENT
# --------------------------
class PaymentSerializer(serializers.ModelSerializer):
    reservation = ReservationSerializer(read_only=True)

    class Meta:
        model = Payment
        fields = ['id', 'reservation', 'amount', 'method', 'status', 'payment_date']

# --------------------------
# INSCRIPTION UTILISATEUR
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
            role='client'
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

# --------------------------
# ADHÉSION
# --------------------------
class MembershipSerializer(serializers.ModelSerializer):
    class Meta:
        model = Membership
        fields = ['start_date', 'expiry_date', 'payment_id']
