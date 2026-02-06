from django.contrib.auth.models import User, Group, Permission
from django.core.management import BaseCommand


class Command(BaseCommand):
    help = "Назначает пользователю с ID=2 права менеджера профилей"

    def handle(self, *args, **options):
        self.stdout.write("=" * 50)
        self.stdout.write("Начало выполнения команды назначения прав")
        self.stdout.write("=" * 50)

        # 1. Находим пользователя
        self.stdout.write("\n1. Поиск пользователя с ID=2...")
        try:
            user = User.objects.get(username="Daria")
            self.stdout.write(
                self.style.SUCCESS(f"✓ Найден пользователь: {user.username}")
            )
        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR("✗ Пользователь с ID=2 не найден!")
            )
            return

        # 2. Находим или создаем группу
        self.stdout.write("\n2. Работа с группой 'profile_manager'...")
        group, created = Group.objects.get_or_create(name="profile_manager")

        if created:
            self.stdout.write(
                self.style.SUCCESS(f"✓ Создана новая группа: {group.name}")
            )
        else:
            self.stdout.write(
                self.style.WARNING(f"✓ Группа уже существует: {group.name}")
            )

        # 3. Находим разрешения
        self.stdout.write("\n3. Поиск необходимых разрешений...")

        try:
            permission_profile = Permission.objects.get(codename="view_profile")
            self.stdout.write(
                self.style.SUCCESS(f"✓ Найдено разрешение: view_profile")
            )
        except Permission.DoesNotExist:
            self.stdout.write(
                self.style.ERROR("✗ Разрешение 'view_profile' не найдено")
            )
            return

        try:
            permission_logentry = Permission.objects.get(codename="view_logentry")
            self.stdout.write(
                self.style.SUCCESS(f"✓ Найдено разрешение: view_logentry")
            )
        except Permission.DoesNotExist:
            self.stdout.write(
                self.style.ERROR("✗ Разрешение 'view_logentry' не найдено")
            )
            return

        # 4. Добавляем разрешение в группу
        self.stdout.write("\n4. Настройка группы...")
        if permission_profile in group.permissions.all():
            self.stdout.write(
                self.style.WARNING("⏭ Разрешение view_profile уже в группе")
            )
        else:
            group.permissions.add(permission_profile)
            self.stdout.write(
                self.style.SUCCESS("✓ Разрешение view_profile добавлено в группу")
            )

        # 5. Добавляем пользователя в группу
        self.stdout.write("\n5. Добавление пользователя в группу...")
        if user in group.user_set.all():
            self.stdout.write(
                self.style.WARNING(f"⏭ Пользователь уже в группе {group.name}")
            )
        else:
            user.groups.add(group)
            self.stdout.write(
                self.style.SUCCESS(f"✓ Пользователь добавлен в группу {group.name}")
            )

        # 6. Добавляем прямое разрешение пользователю
        self.stdout.write("\n6. Назначение прямых разрешений...")
        if permission_logentry in user.user_permissions.all():
            self.stdout.write(
                self.style.WARNING("⏭ Разрешение view_logentry уже у пользователя")
            )
        else:
            user.user_permissions.add(permission_logentry)
            self.stdout.write(
                self.style.SUCCESS("✓ Разрешение view_logentry назначено пользователю")
            )

        # 7. Сохраняем изменения
        self.stdout.write("\n7. Сохранение изменений...")
        group.save()
        user.save()
        self.stdout.write(self.style.SUCCESS("✓ Все изменения сохранены"))

        # 8. Итоговая информация
        self.stdout.write("\n" + "=" * 50)
        self.stdout.write("ИТОГИ НАЗНАЧЕНИЯ ПРАВ")
        self.stdout.write("=" * 50)

        self.stdout.write(f"\nПользователь: {self.style.HTTP_INFO(user.username)}")
        self.stdout.write(f"Группы: {', '.join([g.name for g in user.groups.all()])}")

        self.stdout.write(f"\nГруппа '{group.name}' содержит разрешения:")
        for perm in group.permissions.all():
            self.stdout.write(f"  • {perm.codename} - {perm.name}")

        self.stdout.write("\nПрямые разрешения пользователя:")
        direct_perms = user.user_permissions.all()
        if direct_perms:
            for perm in direct_perms:
                self.stdout.write(f"  • {perm.codename} - {perm.name}")
        else:
            self.stdout.write("  Нет прямых разрешений")

        # Показываем все права пользователя
        self.stdout.write("\nВсе права пользователя (включая групповые):")
        all_perms = user.get_all_permissions()
        for perm in sorted(all_perms):
            self.stdout.write(f"  • {perm}")

        self.stdout.write("\n" + "=" * 50)
        self.stdout.write(self.style.SUCCESS("Команда выполнена успешно!"))
        self.stdout.write("=" * 50)