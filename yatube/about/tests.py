from http import HTTPStatus

from django.test import TestCase, Client
from django.urls import reverse


class AboutURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_about_urls_exist(self):
        """
        Тестирование на существование страниц
        с соответсвующим URL для приложения about.
        """
        templates_url_names = (
            '/about/author/',
            '/about/tech/',
        )

        for url in templates_url_names:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)


class AboutPagesTemplatesTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def setUp(self):
        self.guest_client = Client()

    def test_pages_uses_correct_template(self):
        """
        Тестирование на получение корректного шаблона
        при выполнении view-функциии.
        """
        templates_page_names = {
            reverse('about:author'): 'about/author.html',
            reverse('about:tech'): 'about/tech.html',
        }

        for reverse_name, template in templates_page_names.items():
            with self.subTest(template=template):
                response = self.guest_client.get(reverse_name)
                self.assertTemplateUsed(response, template,
                                        f'Шаблон {template} не соответсвует'
                                        f'views-функции {reverse_name}')
