from django.contrib.auth.models import Group
from rest_framework import serializers


class GroupSerializer(serializers.ModelSerializer):
    """Класс сериализатор описывающий данные модели"""
    permissions = serializers.StringRelatedField(many=True)

    class Meta:
        model = Group
        fields = "pk", "name", "permissions"

