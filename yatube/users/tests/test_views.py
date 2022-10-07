from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from users.forms import CreationForm


User = get_user_model()


class UsersPagesTemplatesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(
            UsersPagesTemplatesTests.user
        )

    def test_pages_uses_correct_template(self):
        templates_page_names = {
            reverse('users:signup'): 'users/signup.html',
            reverse('users:login'): 'users/login.html',
            reverse('users:password_reset'): 'users/password_reset_form.html',
            reverse('users:password_reset_done'): 'users/'
                                                  'password_reset_done.html',
            reverse('users:password_reset_complete'): 'users/password_reset'
                                                      '_complete.html',
            reverse('users:password_change'): 'users/'
                                              'password_change_form.html',
            reverse('users:password_change_done'): 'users/'
                                                   'password_change_done.html',
            reverse('users:logout'): 'users/logged_out.html',
        }
        for reverse_name, template in templates_page_names.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template,
                                        f'Шаблон {template}'
                                        f'не соответсвует'
                                        f'views-функции {reverse_name}')

    def test_user_signup_show_correct_context(self):
        response = self.guest_client.get(reverse('users:signup'))
        self.assertIsInstance(response.context.get('form'), CreationForm)
