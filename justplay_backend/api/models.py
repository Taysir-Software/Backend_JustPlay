from django.db import models
from django.contrib.auth.models import AbstractUser

# -----------------------------
# 1. USER MODEL AVEC ROLE
# -----------------------------
class User(AbstractUser):
    ROLE_CHOICES = (
        ('client', 'Client'),
        ('exploitant', 'Exploitant'),
        ('admin', 'Admin'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='client')

    def __str__(self):
        return self.username

# -----------------------------
# 1. PROFIL EXPLOITANT
# -----------------------------

class ExploitantProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='exploitant_profile')
    company_name = models.CharField(max_length=255)
    logo = models.ImageField(upload_to='exploitants/logos/', null=True, blank=True)
    website = models.URLField(blank=True)
    contact_phone = models.CharField(max_length=30, blank=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.company_name





# -----------------------------
# 2. ACTIVITÉ
# -----------------------------

class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Activity(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    exploitant = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    exploitant_user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name="activities_managed")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    categories = models.ManyToManyField(Category, blank=True, related_name="activities")
    


    def __str__(self):
        return self.name
    
    class Meta:
        indexes = [
            models.Index(fields=["name"]),
            models.Index(fields=["exploitant"]),
            
        ]


# -----------------------------
# 3. IMAGES D’ACTIVITÉS (1:N)
# -----------------------------
class ActivityImage(models.Model):
    activity = models.ForeignKey(Activity, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='activities/')
    uploaded_at = models.DateTimeField(auto_now_add=True)


# -----------------------------
# 4. CRÉNEAU HORAIRE
# -----------------------------
class Timeslot(models.Model):
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    is_booked = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.activity.name} ({self.start_time} - {self.end_time})"


# -----------------------------
# 5. RÉSERVATION
# -----------------------------
class Reservation(models.Model):
    STATUS_CHOICES = (
        ('pending', 'En attente'),
        ('paid', 'Payée'),
        ('cancelled', 'Annulée'),
    )

    SOURCE_CHOICES = (
        ('justplay', 'JustPlay'),
        ('exploitant', 'Exploitant'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    timeslot = models.ForeignKey(Timeslot, on_delete=models.CASCADE)
    reservation_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES, default='justplay')

    def __str__(self):
        return f"Réservation {self.id} - {self.user.username} - {self.status}"


# -----------------------------
# 6. PAIEMENT
# -----------------------------
class Payment(models.Model):
    PAYMENT_METHODS = (
        ('stripe', 'Stripe'),
        ('paypal', 'PayPal'),
        ('cash', 'Cash'),
    )

    PAYMENT_STATUS = (
        ('paid', 'Payé'),
        ('failed', 'Échoué'),
        ('refunded', 'Remboursé'),
    )

    reservation = models.OneToOneField(Reservation, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    status = models.CharField(max_length=10, choices=PAYMENT_STATUS, default='paid')
    payment_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Paiement {self.id} - {self.amount} {self.method}"


# -----------------------------
# 7. AVIS ET COMMENTAIRES
# -----------------------------

class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE)
    rating = models.IntegerField()  # 1 à 5
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


# -----------------------------
# 8. LOG D'ANNULATION
# -----------------------------
class CancellationLog(models.Model):
    reservation = models.ForeignKey(Reservation, on_delete=models.CASCADE)
    cancelled_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    reason = models.TextField(blank=True)
    cancelled_at = models.DateTimeField(auto_now_add=True)


