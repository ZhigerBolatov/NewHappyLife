from rest_framework.serializers import ModelSerializer
from .models import *
from .functions import datetime_serialize


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'iin', 'name', 'surname', 'bio', 'photo', 'telephone', 'email', 'address', 'role',
                  'category', 'price']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['role'] = ROLE_CHOICES[instance.role].capitalize()
        if instance.category:
            representation['category'] = instance.category.name
        return representation


class CategorySerializer(ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class ScheduleSerializer(ModelSerializer):
    class Meta:
        model = Schedule
        fields = '__all__'

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if instance.time_slots:
            representation['time_slots'] = TimeSlotSerializer(instance=instance.time_slots, many=True).data
        return representation


class TimeSlotSerializer(ModelSerializer):
    class Meta:
        model = TimeSlot
        fields = '__all__'

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['starts_at'] = instance.starts_at.strftime("%H:%M")
        representation['ends_at'] = instance.ends_at.strftime("%H:%M")
        return representation


class BookingSerializer(ModelSerializer):
    class Meta:
        model = Booking
        fields = '__all__'

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['datetime'] = datetime_serialize(representation['datetime'])
        representation['patient'] = UserSerializer(instance=instance.patient, many=False).data
        representation['doctor'] = UserSerializer(instance=instance.doctor, many=False).data
        return representation


class UserFullSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name', 'surname', 'bio', 'photo', 'telephone', 'email', 'role', 'category', 'price',
                  'schedule']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['role'] = ROLE_CHOICES[instance.role].capitalize()
        if instance.category:
            representation['category'] = CategorySerializer(instance=instance.category).data
        if instance.schedule:
            representation['schedule'] = ScheduleSerializer(instance=instance.schedule).data
        return representation
