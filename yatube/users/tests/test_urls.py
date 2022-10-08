from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase, Client


User = get_user_model()


class UsersURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(UsersURLTests.user)

    def test_users_url_exists_for_guest_client(self):
        """
        Возможность незарегистрированного пользователя
        посещать страницы.
        """
        templates_url_names = [
            '/auth/signup/',
            '/auth/login/',
            '/auth/password_reset/',
            '/auth/password_reset/done/',
            '/auth/reset/done/',
        ]
        for urls in templates_url_names:
            with self.subTest(urls=urls):
                response = self.guest_client.get(urls)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_users_url_exists_for_user_client(self):
        """
        Возможность зарегистрированного пользователя
        посещать страницы смены пароля и выхода из аккаунта.
        """
        templates_url_names = [
            '/auth/password_change/',
            '/auth/password_change/done/',
            '/auth/logout/',
        ]
        for urls in templates_url_names:
            with self.subTest(urls=urls):
                response = self.authorized_client.get(urls)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_users_url_redirect_for_guest(self):
        """
        Перенаправление незарегистрированного пользователя
        со страницы смены пароля.
        """
        redirect_url = '/auth/login/'
        templates_url_names = {
            '/auth/password_change/': redirect_url,
            '/auth/password_change/done/': redirect_url,
        }
        for in_put_url, redir in templates_url_names.items():
            with self.subTest(in_put_url=in_put_url):
                response = self.guest_client.get(
                    in_put_url,
                    follow=True,
                )
                self.assertRedirects(response, f'{redir}?next={in_put_url}')

    def test_urls_uses_correct_template(self):
        """
        Тестирование на использование корректных
        шаблонов для соответсвующих URL.
        """
        templates_url_names = {
            '/auth/signup/': 'users/signup.html',
            '/auth/login/': 'users/login.html',
            '/auth/password_reset/': 'users/password_reset_form.html',
            '/auth/password_reset/done/': 'users/password_reset_done.html',
            '/auth/reset/done/': 'users/password_reset_complete.html',
            '/auth/password_change/': 'users/password_change_form.html',
            '/auth/password_change/done/': 'users/password_change_done.html',
            '/auth/logout/': 'users/logged_out.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template, f'{response}')
