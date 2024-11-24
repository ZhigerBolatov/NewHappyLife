from django.contrib.auth import login, authenticate, logout
from django.shortcuts import get_object_or_404
from django.db.models import Q

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny

from .serializers import UserSerializer, CategorySerializer
from .models import *
from .tasks import *
from .permissions import *


class AuthAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        iin = request.data.get('iin')
        password = request.data.get('password')
        user = authenticate(request, iin=iin, password=password)
        if user is None:
            return Response(data={'success': False}, status=status.HTTP_400_BAD_REQUEST)
        login(request, user)
        return Response(data={'success': True, 'role': user.role.name}, status=status.HTTP_200_OK)


class LogOutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        logout(request)
        return Response(data={'success': True}, status=status.HTTP_200_OK)


class UserAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        data = UserSerializer(request.user, many=False).data
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
