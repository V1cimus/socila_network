import shutil
import tempfile

from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.conf import settings

from posts.models import Post, Group, Comment


User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group,
        )
        cls.create_post = 'posts:create_post'

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(
            PostCreateFormTest.user
        )

    def test_post_create_form(self):
        """Тестирование на возможность создания поста со всеми параметрами."""
        post_count = Post.objects.count()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Тестовый текст',
            'group': self.group.id,
            'image': uploaded
        }

        response = self.authorized_client.post(
            reverse(self.create_post),
            data=form_data,
        )

        self.assertRedirects(
            response,
            reverse('posts:profile', kwargs={'username': self.user})
        )
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text='Тестовый текст',
                author=self.user,
                group=self.group,
                image='posts/small.gif',
            ).exists()
        )

    def test_post_edit_form(self):
        """
        Тестирование на возможность
        редактировать пост со всеми параметрами.
        """
        post = Post.objects.get(pk=1)
        post_count = Post.objects.count()
        form_data = {
            'text': 'Измененный тестовый текст',
            'group': self.group.id,
        }

        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': post.id}),
            data=form_data,
        )

        self.assertEqual(Post.objects.count(), post_count)
        self.assertRedirects(
            response,
            reverse('posts:post_detail', kwargs={'post_id': post.id})
        )
        self.assertTrue(
            Post.objects.filter(
                text='Измененный тестовый текст',
                author=self.user,
                group=self.group,
            ).exists()
        )

    def test_post_create_nonaut_user(self):
        """
        Тестирование на возможность
        создать пост неавторизованному пользователю.
        """
        post_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый текст',
            'group': self.group.id,
        }

        self.guest_client.post(
            reverse(self.create_post),
            data=form_data,
        )

        self.assertEqual(Post.objects.count(), post_count)


class CommentCreateFormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group,
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(
            CommentCreateFormTest.user
        )

    def test_comment_create_form_non_authorize(self):
        """
        Тестирование на отсутвие возможности оставлять
        комментарии неавторизованым пользователям.
        """
        comment_count = Comment.objects.filter(post__pk=1).count()
        form_data = {
            'text': 'Тестовый комментрарий',
        }
        in_put_url = reverse(
            'posts:add_comment', kwargs={'post_id': self.post.pk}
        )
        redirect_url = reverse('users:login')

        response = self.guest_client.post(
            in_put_url,
            data=form_data,
            follow=True,
        )

        self.assertEqual(
            Comment.objects.filter(post__pk=1).count(),
            comment_count
        )
        self.assertRedirects(
            response,
            f'{redirect_url}?next={in_put_url}'
        )

    def test_comment_create_form(self):
        """
        Тестирование на возможности оставлять
        комментарии авторизованым пользователям.
        """
        comment_count = Comment.objects.filter(post__pk=1).count()
        form_data = {
            'text': 'Тестовый комментрарий',
        }
        in_put_url = reverse(
            'posts:add_comment', kwargs={'post_id': self.post.pk}
        )

        response = self.authorized_client.post(
            in_put_url,
            data=form_data,
            follow=True,
        )

        self.assertRedirects(
            response,
            reverse('posts:post_detail', kwargs={'post_id': self.post.pk})
        )
        self.assertEqual(
            Comment.objects.filter(post__pk=1).count(),
            comment_count + 1
        )
