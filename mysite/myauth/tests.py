
from django.test import TestCase
from django.urls import reverse

class GetCookieViewTestCase(TestCase):
    def test_get_cookie_view(self):
        response = self.client.get(reverse("myauth:cookie_get"))
        self.assertContains(response, "COOKIE VALUE")


class TestViewTest(TestCase):
    def test_test_view(self):
        response = self.client.get(reverse("myauth:test_view"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['content-type'], 'application/json')
        expected_data = {"test1": "test1", "test2": "test2"}
        self.assertEqual(response.json(), expected_data)


