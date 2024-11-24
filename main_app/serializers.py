from rest_framework.serializers import ModelSerializer
from .models import *


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['iin', 'name', 'surname', 'photo', 'telephone', 'email', 'address', 'role', 'category', 'price']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if instance.category:
            representation['category'] = instance.category.name
        return representation


class CategorySerializer(ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'
