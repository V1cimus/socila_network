from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.core.cache import cache

from posts.models import Post, Group


User = get_user_model()


class PostsURLTests(TestCase):
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
        )
        cls.url_index = '/'
        cls.url_group_list = f'/group/{PostsURLTests.group.slug}/'
        cls.url_profile = f'/profile/{PostsURLTests.user}/'
        cls.url_posts = f'/posts/{PostsURLTests.post.pk}/'
        cls.url_post_edit = f'/posts/{PostsURLTests.post.pk}/edit/'
        cls.url_post_create = '/create/'
        cls.unexisting_page = '/unexisting_page/'

    def setUp(self):
        cache.clear()
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(PostsURLTests.user)

    def test_posts_url_exists_at_desired_location(self):
        """
        Тестирование на существование страниц с соответсвующим URL
        для приложения posts неавторизованному пользователю.
        """
        templates_url_names = (
            self.url_index,
            self.url_group_list,
            self.url_profile,
            self.url_posts,
        )
        for url in templates_url_names:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(
                    response.status_code, HTTPStatus.OK,
                    f'Ошибка {url} не существует')

    def test_posts_url_exists_for_author_edit(self):
        """
        Тестирование на существование страниц с соответсвующим URL
        для приложения posts авторизованному пользователю.
        """
        templates_url_names = (
            self.url_index,
            self.url_group_list,
            self.url_profile,
            self.url_posts,
            self.url_post_edit,
            self.url_post_create,
        )

        for urls in templates_url_names:
            with self.subTest(urls=urls):
                response = self.authorized_client.get(urls)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_posts_url_redirect_for_guest_edit(self):
        """
        Тестирование на перенаправление неавторизованного пользователя
        на страницу логина при переходе по URL на редактирование поста.
        """
        in_put_url = self.url_post_edit
        redirect_url = '/auth/login/'

        response = self.guest_client.get(
            in_put_url,
            follow=True,
        )

        self.assertRedirects(response, f'{redirect_url}?next={in_put_url}')

    def test_posts_url_redirect_for_non_author_edit(self):
        """
        Тестирование на перенаправление авторизованного
        пользователя (не автора) на страницу поста при
        переходе по URL на редактирование поста.
        """
        user_non_author = User.objects.create_user(username='non_auth')
        authorized_client_non_auth = Client()
        authorized_client_non_auth.force_login(user_non_author)
        in_put_url = self.url_post_edit
        redirect_url = self.url_posts

        response = authorized_client_non_auth.get(
            in_put_url,
            follow=True,
        )

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, 'posts/post_detail.html')
        self.assertRedirects(response, redirect_url)

    def test_unexisting_page_404(self):
        """
        Тестирование на несуществующую страницу.
        """
        response = self.guest_client.get(self.unexisting_page)

        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_urls_uses_correct_template(self):
        """
        Тестирование на использование корректных шаблонов.
        """
        templates_url_names = {
            self.url_index: 'posts/index.html',
            self.url_group_list: 'posts/group_list.html',
            self.url_profile: 'posts/profile.html',
            self.url_posts: 'posts/post_detail.html',
            self.url_post_edit: 'posts/create_post.html',
            self.url_post_create: 'posts/create_post.html',
            self.unexisting_page: 'core/404.html',
        }

        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)
