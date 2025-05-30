# from django.contrib import admin
# from .models import User, Activity, ActivityImage, Timeslot, Reservation, Payment
# # Register your models here.


# admin.site.register(User)
# admin.site.register(Activity)
# admin.site.register(ActivityImage)
# admin.site.register(Timeslot)
# admin.site.register(Reservation)
# admin.site.register(Payment)

from django.contrib import admin
from django.utils.html import format_html
from .models import User, Activity, ActivityImage, Timeslot, Reservation, Payment, Category, Review, CancellationLog, ExploitantProfile


# -------------------------
# 1. ADMIN USER
# -------------------------
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'role', 'is_staff', 'is_active']
    list_filter = ['role', 'is_active', 'is_staff']
    search_fields = ['username', 'email']


# -------------------------
# 2. ADMIN ACTIVITÉ
# -------------------------
@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ['name', 'exploitant', 'is_active']
    list_filter = ['is_active', 'exploitant']
    search_fields = ['name', 'exploitant']
    ordering = ['name']


# -------------------------
# 3. ADMIN IMAGE ACTIVITÉ
# Affiche l’image directement
# -------------------------
@admin.register(ActivityImage)
class ActivityImageAdmin(admin.ModelAdmin):
    list_display = ['activity', 'uploaded_at', 'thumbnail']
    readonly_fields = ['thumbnail']
    list_filter = ['activity']
    fields = ['activity', 'image', 'thumbnail']


    def thumbnail(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="100" height="60" />', obj.image.url)
        return "No Image"

    thumbnail.short_description = 'Aperçu'



# admin.site.register(Timeslot)
# admin.site.register(Reservation)
# admin.site.register(Payment)
# admin.site.register(Category)

# ------------------------- 
# 4. ADMIN CRÉNEAU HORAIRE
# -------------------------
@admin.register(Timeslot)
class TimeslotAdmin(admin.ModelAdmin):
    list_display = ('activity', 'start_time', 'end_time', 'is_booked')
    list_filter = ('activity', 'is_booked')
    ordering = ('start_time',)

# -------------------------
# 5. ADMIN RÉSERVATION
# -------------------------

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('user', 'timeslot', 'status', 'reservation_date', 'source')
    list_filter = ('status', 'source', 'reservation_date')
    search_fields = ('user__username',)

# -------------------------
# 6. ADMIN PAIEMENT
# -------------------------

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('reservation', 'amount', 'method', 'status', 'payment_date')
    list_filter = ('method', 'status', 'payment_date')

# -------------------------
# 7. ADMIN CATÉGORIE
# -------------------------

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

# -------------------------
# 8. ADMIN REVIEW
# -------------------------

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'activity', 'rating', 'created_at')
    search_fields = ('user__username', 'activity__name')
    list_filter = ('rating', 'created_at')


# -------------------------
# 9. ADMIN LOG D'ANNULATION
# -------------------------

@admin.register(CancellationLog)
class CancellationLogAdmin(admin.ModelAdmin):
    list_display = ('reservation', 'cancelled_by', 'cancelled_at')
    search_fields = ('reservation__id', 'cancelled_by__username')
    list_filter = ('cancelled_at',)

# -------------------------
# 10. ADMIN PROFIL EXPLOITANT
# -------------------------

@admin.register(ExploitantProfile)
class ExploitantProfileAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'user', 'contact_phone')
    search_fields = ('company_name', 'user__username')

# -------------------------
# CONFIGURATION DU PORTAIL D'ADMINISTRATION
# -------------------------

admin.site.site_header = "JustPlay Admin"
admin.site.site_title = "JustPlay Admin Portal"
admin.site.index_title = "Bienvenue dans le portail d'administration JustPlay"

