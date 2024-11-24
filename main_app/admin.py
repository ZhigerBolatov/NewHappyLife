from django.contrib import admin
from .models import *


admin.site.register([
    User,
    ResetPasswordToken,
    Category,
    TimeSlot,
    Schedule,
    Booking
])
