from django.contrib.auth import login, authenticate, logout
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.db import IntegrityError
from django.utils import timezone

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny

import os
from datetime import timedelta

from .serializers import *
from .models import *
from .tasks import *
from .permissions import *


class LogOutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        logout(request)
        return Response(data={'success': True}, status=status.HTTP_200_OK)


class RegistrationApiView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        check_email = User.objects.filter(email=request.data['email'])
        if len(check_email) > 0:
            return Response(data={'success': False, 'field': 'email'}, status=status.HTTP_400_BAD_REQUEST)

        check_telephone = User.objects.filter(telephone=request.data['telephone'])
        if len(check_telephone) > 0:
            return Response(data={'success': False, 'field': 'telephone'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.create_user(iin=request.data['iin'], password=request.data['password'])
        except IntegrityError:
            return Response(data={'success': False, 'field': 'iin'}, status=status.HTTP_400_BAD_REQUEST)

        request.data['role'] = 'PT'
        user = UserSerializer(instance=user, data=request.data, partial=True)
        if user.is_valid():
            user.save()
            return Response(data={'success': True}, status=status.HTTP_200_OK)
        return Response(data={'success': False, 'detail': user.errors}, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        user = User.objects.filter(email=email).first()
        if user:
            random_token = os.urandom(3).hex()[:6]
            reset_password_token = ResetPasswordToken(user=user, token=random_token)
            reset_password_token.save()
            message = (f"User on happylifes.org requested a reset password. "
                       f"If it was not you, please ignore this mail\n\n"
                       f"Your reset token: {random_token}\n\n"
                       f"Generation Time: {reset_password_token.created_at}\n"
                       f"You have 10 minutes to use this token, otherwise it would be bot valid!")
            send_notification_mail(email, message)
            return Response(data={'success': True}, status=status.HTTP_200_OK)
        return Response(data={'success': False}, status=status.HTTP_400_BAD_REQUEST)


class SetNewPasswordAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        user = User.objects.filter(email=email).first()
        if user:
            token = request.data.get('token')
            reset_password_token = ResetPasswordToken.objects.filter(Q(user=user) & Q(token=token)).first()
            if not reset_password_token:
                return Response(data={'success': False,
                                      'detail': 'Email and/or Token is not valid!'},
                                status=status.HTTP_400_BAD_REQUEST)

            if timezone.now() - reset_password_token.created_at > timedelta(minutes=10):
                return Response(data={'success': False,
                                      'detail': 'Token was expired!'},
                                status=status.HTTP_400_BAD_REQUEST)

            new_password = request.data.get('new_password')
            user.set_password(new_password)
            user.save()
            reset_password_token.delete()
            return Response(data={'success': True,
                                  'detail': 'Password successfully updated!'},
                            status=status.HTTP_200_OK)

        return Response(data={'success': False,
                              'detail': 'Email and/or Token is not valid!'},
                        status=status.HTTP_400_BAD_REQUEST)


class UserAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        data = UserSerializer(User.objects.get(id=1), many=False).data
        return Response(data=data, status=status.HTTP_200_OK)


class StatsApiView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        patients = User.objects.filter(role='PT')
        doctors = User.objects.filter(role='DC')
        admins = User.objects.filter(role='AD')
        data = {
            'patients_count': len(patients),
            'doctors_count': len(doctors),
            'staff_count': len(doctors) + len(admins),
        }
        return Response(data=data, status=status.HTTP_200_OK)


class CategoryApiView(APIView):
    permission_classes = [IsAdminOrReadOnly]

    def get(self, request):
        categories = Category.objects.all()
        data = CategorySerializer(instance=categories, many=True).data
        return Response(data=data, status=status.HTTP_200_OK)


class DoctorApiView(APIView):
    permission_classes = [IsAdminOrReadOnly]

    def get(self, request):
        doctors = User.objects.filter(role='DC')
        data = UserSerializer(instance=doctors, many=True).data
        return Response(data=data, status=status.HTTP_200_OK)


class DoctorSearchApiView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        name = request.GET.get('name')
        category = request.GET.get('category')
        if name is not None and category is not None:
            doctors = User.objects.filter(Q(name__icontains=name) | Q(surname__icontains=name))
            doctors = doctors.filter(Q(category=category))
        elif name is not None:
            doctors = User.objects.filter(Q(name__icontains=name) | Q(surname__icontains=name))
        elif category is not None:
            doctors = User.objects.filter(Q(category=category))
        else:
            doctors = User.objects.all()
        data = UserSerializer(instance=doctors, many=True).data
        return Response(data=data, status=status.HTTP_200_OK)


class DoctorDetailApiView(APIView):
    permission_classes = [IsAdminOrReadOnly]

    def get(self, request, doctor_id):
        doctor = get_object_or_404(User, id=doctor_id)
        data = UserSerializer(instance=doctor).data
        return Response(data=data, status=status.HTTP_200_OK)

    def patch(self, request, doctor_id):
        doctor = get_object_or_404(User, id=doctor_id)
        mutable_data = request.data.copy()
        if request.data.get('category') == '0':
            mutable_data['category'] = None
        if request.data.get('schedule') == '0':
            mutable_data['schedule'] = None
        doctor = UserSerializer(instance=doctor, data=mutable_data, partial=True)
        if doctor.is_valid():
            doctor.save()
            return Response(data=doctor.data, status=status.HTTP_200_OK)
        return Response(data=doctor.errors, status=status.HTTP_400_BAD_REQUEST)


class DoctorScheduleApiView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, doctor_id):
        doctor = get_object_or_404(User, id=doctor_id)
        data = ScheduleSerializer(instance=doctor.schedule).data
        bookings = Booking.objects.filter(doctor=doctor)
        data.update({'bookings': BookingSerializer(instance=bookings, many=True).data})
        return Response(data=data, status=status.HTTP_200_OK)


class NewslettersApiView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        try:
            NewsletterFollower.objects.get(email=email)
        except NewsletterFollower.DoesNotExist:
            newsletter_follower = NewsletterFollower(email=email)
            newsletter_follower.save()
            return Response(data={'success': True}, status=status.HTTP_200_OK)
        else:
            return Response(data={'success': False, 'detail': 'Email already following!'},
                            status=status.HTTP_400_BAD_REQUEST)


class BookingApiView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role == 'PT':
            patient = request.user.id
            bookings = Booking.objects.filter(patient=patient).filter(status='Accepted').order_by('datetime')
            data = BookingSerializer(instance=bookings, many=True).data
        elif request.user.role == 'DC':
            doctor = request.user.id
            today = timezone.localtime().date()
            bookings = Booking.objects.filter(doctor=doctor, datetime=today).filter(status='Accepted').order_by('datetime')
            if 'datetime' in request.GET:
                bookings = bookings.filter(datetime__icontains=request.GET.get('datetime'))
            if 'patient' in request.GET:
                patients = User.objects.filter(role='PT')
                patients_by_iin = patients.filter(iin__icontains=request.GET.get('patient'))
                patients_by_name = patients.filter(name__icontains=request.GET.get('patient'))
                patients_by_surname = patients.filter(surname__icontains=request.GET.get('patient'))
                patients = patients_by_iin | patients_by_name | patients_by_surname
                new_bookings = []
                for booking in bookings:
                    if booking.patient in patients:
                        new_bookings.append(booking)
                bookings = new_bookings
            data = BookingSerializer(instance=bookings, many=True).data
        elif request.user.role == 'AD':
            today = timezone.localtime().date()
            if 'datetime' in request.GET:
                bookings = Booking.objects.filter(status='Accepted', datetime__icontains=request.GET.get('datetime'))
            else:
                bookings = Booking.objects.filter(status='Accepted', datetime=today).order_by('datetime')
            if 'patient' in request.GET:
                patients = User.objects.filter(role='PT')
                patients_by_iin = patients.filter(iin__icontains=request.GET.get('patient'))
                patients_by_name = patients.filter(name__icontains=request.GET.get('patient'))
                patients_by_surname = patients.filter(surname__icontains=request.GET.get('patient'))
                patients = patients_by_iin | patients_by_name | patients_by_surname
                new_bookings = []
                for booking in bookings:
                    if booking.patient in patients:
                        new_bookings.append(booking)
                bookings = new_bookings
            data = BookingSerializer(instance=bookings, many=True).data
        return Response(data=data, status=status.HTTP_200_OK)

    def post(self, request):
        request.data['patient'] = request.user.id
        booking = BookingSerializer(data=request.data)
        if booking.is_valid():
            booking.save()
            return Response(data={'success': True}, status=status.HTTP_200_OK)
        return Response(data={'success': False, 'detail': booking.errors}, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request):
        booking = get_object_or_404(Booking, id=request.data.get('id'))
        booking = BookingSerializer(instance=booking, data=request.data, partial=True)
        if booking.is_valid():
            booking.save()
            return Response(data={'success': True}, status=status.HTTP_200_OK)
        return Response(data={'success': False, 'detail': booking.errors}, status=status.HTTP_400_BAD_REQUEST)


class HistoryApiView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        booking_id = request.GET.get('id')
        if booking_id is not None:
            booking = get_object_or_404(Booking, id=booking_id)
            data = BookingSerializer(instance=booking, many=False).data
            return Response(data=data, status=status.HTTP_200_OK)
        if request.user.role == 'PT':
            patient = request.user.id
            booking = Booking.objects.filter(patient=patient).exclude(status='Accepted').order_by('-datetime')
            data = BookingSerializer(instance=booking, many=True).data
        elif request.user.role == 'DC':
            doctor = request.user.id
            booking = Booking.objects.filter(doctor=doctor).exclude(status='Accepted').order_by('-datetime')
            data = BookingSerializer(instance=booking, many=True).data
        return Response(data=data, status=status.HTTP_200_OK)


class RejectBookingApiView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        request.user.role = 'AD'
        if request.user.role == 'PT':
            patient = request.user.id
            booking = Booking.objects.filter(patient=patient).get(id=request.data.get('id'))
            booking.status = 'Rejected'
            current_time = timezone.localtime(timezone.now())
            time_difference = (current_time - booking.datetime).seconds
            if time_difference < 1800:
                return Response(data={'success': False,
                                      'detail': 'You can`t cancel appointment less than 30 minutes in advance.'},
                                status=status.HTTP_400_BAD_REQUEST)
            booking.description = f'Appointment rejected by patient at {current_time.strftime('%d-%m-%Y, %H:%M')}'
            booking.save()
            return Response(data={'success': True}, status=status.HTTP_200_OK)
        elif request.user.role == 'AD':
            booking = Booking.objects.get(id=request.data.get('id'))
            booking.status = 'Rejected'
            current_time = timezone.localtime(timezone.now())
            time_difference = (current_time - booking.datetime).seconds
            if time_difference < 1800:
                return Response(data={'success': False,
                                      'detail': 'You can`t cancel appointment less than 30 minutes in advance.'},
                                status=status.HTTP_400_BAD_REQUEST)
            booking.description = request.data.get('description')
            booking.save()
            return Response(data={'success': True}, status=status.HTTP_200_OK)


class AcceptBookingApiView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        doctor = request.user.id
        booking = Booking.objects.filter(doctor=doctor).get(id=request.data.get('id'))
        booking.status = 'Done'
        booking.save()
        return Response(data={'success': True}, status=status.HTTP_200_OK)


class StatisticsApiView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        request.user.role = 'AD'
        if request.user.role == 'DC':
            statistics_type = request.GET.get('type')
            if statistics_type == 'datetime':
                datetime = request.GET.get('datetime')
                bookings = Booking.objects.filter(doctor=request.user.id, datetime__icontains=datetime)
            elif statistics_type == 'week':
                today = timezone.localtime().date()
                last_week = timezone.localtime().date() - timedelta(days=7)
                bookings = Booking.objects.filter(doctor=request.user.id).filter(datetime__lte=today,
                                                                                 datetime__gte=last_week)
            elif statistics_type == 'month':
                today = timezone.localtime().date()
                last_month = today.replace(day=1) - timedelta(days=1)
                bookings = Booking.objects.filter(doctor=request.user.id).filter(datetime__lte=today,
                                                                                 datetime__gte=last_month)
            else:
                bookings = Booking.objects.filter(doctor=request.user.id)
            accepted = len(bookings.filter(status='Accepted'))
            rejected = len(bookings.filter(status='Rejected'))
            done = len(bookings.filter(status='Done'))
            data = {
                'all': len(bookings),
                'accepted': accepted,
                'rejected': rejected,
                'done': done
            }
            return Response(data=data, status=status.HTTP_200_OK)
        elif request.user.role == 'AD':
            statistics_type = request.GET.get('type')
            if statistics_type == 'datetime':
                datetime = request.GET.get('datetime')
                bookings = Booking.objects.filter(datetime__icontains=datetime)
            elif statistics_type == 'week':
                today = timezone.localtime().date()
                last_week = timezone.localtime().date() - timedelta(days=7)
                bookings = Booking.objects.filter(datetime__lte=today, datetime__gte=last_week)
            elif statistics_type == 'month':
                today = timezone.localtime().date()
                last_month = today.replace(day=1) - timedelta(days=1)
                bookings = Booking.objects.filter(datetime__lte=today, datetime__gte=last_month)
            else:
                bookings = Booking.objects.all()
            doctor_id = request.GET.get('id')
            if doctor_id is not None:
                bookings = bookings.filter(doctor=doctor_id)
            accepted = len(bookings.filter(status='Accepted'))
            rejected = len(bookings.filter(status='Rejected'))
            done = len(bookings.filter(status='Done'))
            data = {
                'all': len(bookings),
                'accepted': accepted,
                'rejected': rejected,
                'done': done
            }
            return Response(data=data, status=status.HTTP_200_OK)


class DoctorRegistrationApiView(APIView):
    permission_classes = [IsAdminOrReadOnly]

    def post(self, request):
        check_email = User.objects.filter(email=request.data['email'])
        if len(check_email) > 0:
            return Response(data={'success': False, 'field': 'email'}, status=status.HTTP_400_BAD_REQUEST)

        check_telephone = User.objects.filter(telephone=request.data['telephone'])
        if len(check_telephone) > 0:
            return Response(data={'success': False, 'field': 'telephone'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.create_user(iin=request.data['iin'], password=request.data['password'])
        except IntegrityError:
            return Response(data={'success': False, 'field': 'iin'}, status=status.HTTP_400_BAD_REQUEST)

        multable_query_dict = request.data.copy()
        multable_query_dict.update({'role': 'DC'})
        user = UserSerializer(instance=user, data=multable_query_dict, partial=True)
        if user.is_valid():
            user.save()
            return Response(data={'success': True}, status=status.HTTP_200_OK)
        return Response(data={'success': False, 'detail': user.errors}, status=status.HTTP_400_BAD_REQUEST)


class ScheduleApiView(APIView):
    permission_classes = [IsAdminOrReadOnly]

    def get(self, request):
        schedules = Schedule.objects.all()
        data = ScheduleSerializer(instance=schedules, many=True).data
        return Response(data=data, status=status.HTTP_200_OK)

    def patch(self, request):
        schedule_data = request.data.get('schedule')
        time_slots_data = request.data.get('time_slots')
        schedule = get_object_or_404(Schedule, id=schedule_data['id'])
        schedule = ScheduleSerializer(instance=schedule, data=schedule_data, partial=True)
        if schedule.is_valid():
            schedule.save()
        else:
            return Response(data=schedule.errors, status=status.HTTP_400_BAD_REQUEST)
        for item in time_slots_data:
            if item['id'] != 'null':
                time_slot = get_object_or_404(TimeSlot, id=item['id'])
                if item['starts_at'] and item['ends_at']:
                    time_slot = TimeSlotSerializer(instance=time_slot, data=item)
                    if time_slot.is_valid():
                        time_slot.save()
                    else:
                        return Response(data=time_slot.errors, status=status.HTTP_400_BAD_REQUEST)
                else:
                    time_slot.delete()
            elif item['starts_at'] and item['ends_at']:
                time_slot = TimeSlotSerializer(data=item)
                if time_slot.is_valid():
                    time_slot.save()
                    schedule = get_object_or_404(Schedule, id=schedule_data['id'])
                    schedule.time_slots.add(time_slot.data.get('id'))
                    schedule.save()
                else:
                    return Response(data=time_slot.errors, status=status.HTTP_400_BAD_REQUEST)
        schedule = get_object_or_404(Schedule, id=schedule_data['id'])
        data = ScheduleSerializer(instance=schedule).data
        return Response(data=data, status=status.HTTP_200_OK)


class AuthAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        if request.user and request.user.is_authenticated:
            return Response(data={'is_authenticated': True, 'role': request.user.role}, status=status.HTTP_200_OK)
        return Response(data={'is_authenticated': False, 'role': None}, status=status.HTTP_200_OK)

    def post(self, request):
        iin = request.data.get('iin')
        password = request.data.get('password')
        user = authenticate(request, iin=iin, password=password)
        if user is None:
            return Response(data={'success': False}, status=status.HTTP_400_BAD_REQUEST)
        login(request, user)
        return Response(data={'success': True, 'role': user.role}, status=status.HTTP_200_OK)
