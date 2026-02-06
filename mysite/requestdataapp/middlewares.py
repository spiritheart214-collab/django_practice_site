import time
from typing import Callable, Dict, List

from django.http import HttpRequest, HttpResponse


class ThrottlingMiddleware:
    """
    Middleware для ограничения частоты запросов от пользователей.

    Ограничивает количество запросов с одного IP-адреса в заданный промежуток времени.
    Если пользователь делает запросы слишком часто, возвращает ошибку 429 (Too Many Requests).

    Attributes:
        get_response: Callable для получения response
        requests: Словарь для хранения истории запросов {ip: [время_запросов]}
        limit: Максимальное количество разрешенных запросов
        window: Временное окно в секундах для подсчета запросов
    """

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]):
        self.get_response: Callable[[HttpRequest], HttpResponse] = get_response
        # {ip: [время_запросов]} - храним время всех запросов для каждого IP
        self.requests: Dict[str, List[float]] = {}
        self.limit: int = 15  # 15 запросов максимум
        self.window: int = 60  # за 60 секунд

    def __call__(self, request: HttpRequest) -> HttpResponse:
        """
        Обрабатывает каждый входящий запрос и применяет throttling.

        Args:
            request: Входящий HTTP запрос

        Returns:
            HTTP ответ или ошибку 429 при превышении лимита
        """
        # Просто получаем IP из request.META
        ip: str = request.META.get('REMOTE_ADDR', 'unknown')
        current_time: float = time.time()

        print(f"Запрос от IP: {ip}")

        # Инициализируем список для нового IP
        if ip not in self.requests:
            self.requests[ip] = []

        # Удаляем старые запросы (которые были больше 10 секунд назад)
        # Генератор списка с условием - оставляем только свежие запросы
        self.requests[ip] = [
            req_time for req_time in self.requests[ip]
            if current_time - req_time < self.window
        ]

        current_count: int = len(self.requests[ip])
        print(f"За последние {self.window} секунд: {current_count} запросов")

        if current_count >= self.limit:
            print(f"ЛИМИТ! Максимум {self.limit} запросов за {self.window} секунд")
            return HttpResponse(
                f"Слишком много запросов! Максимум {self.limit} запросов за {self.window} секунд",
                status=429
            )
        # Добавляем текущий запрос в историю
        self.requests[ip].append(current_time)
        print(f"Запрос разрешен. Счетчик: {len(self.requests[ip])}/{self.limit}")

        # Продолжаем стандартную обработку запроса
        response: HttpResponse = self.get_response(request)
        return response

class CountRequestsMiddleware:
    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]):
        self.get_response: Callable[[HttpRequest], HttpResponse] = get_response
        self.requests_count = 0
        self.response_count = 0
        self.exaptions_count = 0

    def __call__(self, request: HttpRequest):
        self.requests_count += 1
        print("requests_count -", self.requests_count)
        response = self.get_response(request)
        self.response_count += 1
        print("response_count -", self.response_count)

        return response

    def process_exception(self, request: HttpRequest, exaption: Exception):
        self.exaptions_count += 1
        print(f"Got {self.exaptions_count} exceptions")


def set_useragent_on_request_middleware(get_response: Callable[[HttpRequest], HttpResponse]):
    """Middleware для логирования запросов"""
    print("INITIAL CALL - эта строка выполняется ОДИН РАЗ при запуске сервера")
    def middleware(request: HttpRequest):
        print("\n", end="")
        print("=" * 15, "Middleware",  "=" * 15)
        print("Выполняется middleware - set_useragent_on_request_middleware")

        print("request.method -", request)
        request.user_agent = request.META.get("HTTP_USER_AGENT")
        print("Получен HTTP_USER_AGENT -", request.user_agent)
        response = get_response(request)
        print("Завершение middleware")
        print("=" * 30, "\n")

        return response
    return middleware
