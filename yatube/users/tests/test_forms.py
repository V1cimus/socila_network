from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse


User = get_user_model()


class PostCreateFormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def setUp(self):
        self.guest_client = Client()

    def test_post_create_form(self):
        user_count = User.objects.count()
        form_data = {
            'first_name': 'Имя',
            'last_name': 'Фамилия',
            'username': 'admin',
            'email': 'zxc@mail.ru',
            'password1': '123zxc456',
            'password2': '123zxc456',
        }
        response = self.guest_client.post(
            reverse('users:signup'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse('posts:index')
        )
        self.assertEqual(User.objects.count(), user_count + 1)
        self.assertTrue(
            User.objects.filter(
                first_name='Имя',
                username='admin'
            ).exists()
        )
