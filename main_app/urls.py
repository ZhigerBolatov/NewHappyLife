from django.urls import path
from .views import *


urlpatterns = [
    path('auth', AuthAPIView.as_view()),
    path('log_out', LogOutAPIView.as_view()),
    path('register', RegistrationApiView.as_view()),
    path('reset_password', PasswordResetAPIView.as_view()),
    path('set_new_password', SetNewPasswordAPIView.as_view()),
    path('user', UserAPIView.as_view()),
    path('stats', StatsApiView.as_view()),
    path('categories', CategoryApiView.as_view()),
    path('doctors', DoctorApiView.as_view()),
    path('doctors_search', DoctorSearchApiView.as_view()),
    path('doctors_detail/<int:doctor_id>', DoctorDetailApiView.as_view()),
    path('doctors_schedule/<int:doctor_id>', DoctorScheduleApiView.as_view()),
    path('newsletters', NewslettersApiView.as_view()),
    path('booking', BookingApiView.as_view()),
    path('booking_history', HistoryApiView.as_view()),
    path('reject_booking', RejectBookingApiView.as_view()),
    path('accept_booking', AcceptBookingApiView.as_view()),
    path('statistics', StatisticsApiView.as_view()),
    path('doctor_register', DoctorRegistrationApiView.as_view()),
    path('schedule', ScheduleApiView.as_view()),
    path('chat', OpenAIChatAPIView.as_view()),
    path('user_chat', OpenAIUserChatAPIView.as_view()),
    path('booked_booking', BookedBookingApiView.as_view()),
]
