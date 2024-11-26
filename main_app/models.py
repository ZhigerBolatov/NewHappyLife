from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from .managers import UserManager


ROLE_CHOICES = {
    'AD': 'admin',
    'DC': 'doctor',
    'PT': 'patient'
}

STATUS_CHOICES = {
    'AC': 'Accepted',
    'RJ': 'Rejected',
    'DN': 'Done'
}

WEEK_DAY_CHOICES = {
    'Mon': 'Monday',
    'Tue': 'Tuesday',
    'Wed': 'Wednesday',
    'Thu': 'Thursday',
    'Fri': 'Friday',
    'Sat': 'Saturday',
    'Sun': 'Sunday',
}


class User(AbstractBaseUser, PermissionsMixin):
    iin = models.CharField(max_length=12, unique=True)
    name = models.CharField(max_length=255)
    surname = models.CharField(max_length=255)
    bio = models.TextField(null=True, blank=True)
    photo = models.ImageField(upload_to='users', null=True, blank=True)
    telephone = models.CharField(max_length=20, unique=True)
    email = models.CharField(max_length=255, unique=True)
    address = models.TextField(null=True, blank=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)

    category = models.ForeignKey('Category', blank=True, null=True, on_delete=models.PROTECT)
    schedule = models.ForeignKey('Schedule', blank=True, null=True, on_delete=models.PROTECT)
    price = models.PositiveIntegerField(null=True, blank=True)

    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    USERNAME_FIELD = 'iin'
    REQUIRED_FIELDS = []
    objects = UserManager()

    class Meta:
        verbose_name = "user"
        verbose_name_plural = "users"

    def __str__(self):
        return self.iin


class ResetPasswordToken(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    token = models.CharField(max_length=64)
    created_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "reset password token"
        verbose_name_plural = "reset password tokens"

    def __str__(self):
        return str(self.user)


class Category(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()

    class Meta:
        verbose_name = "category"
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name


class TimeSlot(models.Model):
    week_day = models.CharField(max_length=10, choices=WEEK_DAY_CHOICES)
    starts_at = models.TimeField()
    ends_at = models.TimeField()

    class Meta:
        verbose_name = "time slot"
        verbose_name_plural = "time slots"

    def __str__(self):
        return f'{self.week_day}: {self.starts_at} - {self.ends_at}'


class Schedule(models.Model):
    name = models.CharField(max_length=255)
    time_slots = models.ManyToManyField('TimeSlot', blank=True)

    class Meta:
        verbose_name = "schedule"
        verbose_name_plural = "schedules"

    def __str__(self):
        return self.name


class Booking(models.Model):
    patient = models.ForeignKey('User', related_name='patient_booking', on_delete=models.CASCADE)
    doctor = models.ForeignKey('User', related_name='doctor_booking', on_delete=models.CASCADE)
    datetime = models.DateTimeField()

    class Meta:
        verbose_name = "booking"
        verbose_name_plural = "bookings"

    def __str__(self):
        return f'{self.patient} - {self.datetime}'


class NewsletterFollower(models.Model):
    email = models.EmailField(unique=True)

    class Meta:
        verbose_name = "newsletter follower"
        verbose_name_plural = "newsletter followers"

    def __str__(self):
        return self.email
