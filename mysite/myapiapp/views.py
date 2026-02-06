from django.contrib.auth.models import Group, Permission
from rest_framework import status
from rest_framework.generics import ListCreateAPIView
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.views import APIView

from .serializers import GroupSerializer


class HelloWorldView(APIView):
    """Простой класс для тестирования API."""

    def get(self, request: Request) -> Response:
        """Обработка GET запроса. Возвращает JSON с сообщением."""
        return Response({"message": "Hello, World!"})


class GroupListView(ListCreateAPIView):
    """Все группы приложения"""
    queryset = Group.objects.all()
    serializer_class = GroupSerializer

    def post(self, request: Request) -> Response:
        """Обработка POST запроса. Создает новую группу"""

        # 1. Получаем данные из запроса
        group_name = request.data.get('name')  # <- извлекаем 'name' из JSON

        # 2. Проверяем, что имя передано
        if not group_name:
            return Response(
                {"error": "Имя группы обязательно"},
                status=status.HTTP_400_BAD_REQUEST  # статус 400
            )

        # 3. Проверяем, что группа с таким именем не существует
        if Group.objects.filter(name=group_name).exists():
            return Response(
                {"error": f"Группа '{group_name}' уже существует"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 4. Создаем новую группу
        group = Group.objects.create(name=group_name)
        base_permission_codenames = [
            'view_group',  # просмотр групп
            'add_permission',  # добавление разрешений
            'view_permission',  # просмотр разрешений
            'change_permission'# изменение разрешений
        ]

        base_permissions = Permission.objects.filter(codename__in=base_permission_codenames)
        group.permissions.add(*base_permissions)

        group_serializer = GroupSerializer(group)

        # 5. Возвращаем успешный ответ
        return Response({
            "message": "Группа успешно создана",
            "group": group_serializer.data
        }, status=status.HTTP_201_CREATED)  # статус 201
