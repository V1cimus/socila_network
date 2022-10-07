from django.contrib.auth import get_user_model
from django.test import TestCase

from posts.models import Group, Post


User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост текстом более чем 15 символов',
        )

    def test_models_have_correct_object_names(self):
        """Тестирование моделей на передачу корректных имен объектов."""
        group = PostModelTest.group
        post = PostModelTest.post
        field_verboses = {
            group: group.title,
            post: post.text[:15],
        }

        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(expected_value, str(field))

    def test_verbose_name(self):
        """
        Тестирование моделей на передачу
        корректных имен объектов пользователю.
        """
        post = PostModelTest.post
        field_verboses = {
            'text': 'Текст поста',
            'created': 'Дата создания',
            'author': 'Автор',
            'group': 'Группа',
        }

        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).verbose_name, expected_value)

    def test_help_text(self):
        """
        Тестирование моделей на передачу корректного
        вспомогательного текста объектов пользователю.
        """
        post = PostModelTest.post
        field_verboses = {
            'text': 'Введите текст поста',
            'group': 'Группа, к которой будет относиться пост',
        }

        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).help_text, expected_value)
