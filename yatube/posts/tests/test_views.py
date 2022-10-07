import shutil
import tempfile

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.conf import settings
from django.core.cache import cache

from posts.models import Post, Group
from posts.forms import PostForm


User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


class PostsPagesTemplatesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cache.clear()

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(
            PostsPagesTemplatesTests.user
        )
        self.post = Post.objects.create(
            author=self.user,
            text='Тестовый пост',
        )

    def tearDown(self):
        cache.clear()

    def test_pages_uses_correct_template(self):
        """
        Тестирование на существование
        соответсвующим URL с HTML Шаблонами.
        """
        templates_page_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list', kwargs={'slug': self.group.slug}):
            ('posts/group_list.html'),
            reverse('posts:profile', kwargs={'username': self.user.username}):
            ('posts/profile.html'),
            reverse('posts:post_detail', kwargs={'post_id': self.post.pk}):
            ('posts/post_detail.html'),
            reverse('posts:create_post'): 'posts/create_post.html',
            reverse('posts:post_edit', kwargs={'post_id': self.post.pk}):
            ('posts/create_post.html'),
        }

        for reverse_name, template in templates_page_names.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template,
                                        f'Шаблон {template} не соответсвует'
                                        f' views-функции {reverse_name}')

    def test_cache_index_page(self):
        """Тестирование на обновление кэша."""
        response = self.guest_client.get(reverse('posts:index'))

        self.post.delete()

        response_after_del_post = self.guest_client.get(reverse('posts:index'))

        cache.clear()

        response_after_cache_clear = self.guest_client.get(
            reverse('posts:index')
        )

        self.assertEqual(response_after_del_post.content, response.content)
        self.assertNotEqual(
            response_after_cache_clear.content,
            response.content
        )


class PostsPagesContextTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.user_for_second_auth = User.objects.create_user(username='auth-2')
        cls.group_for_paginator = Group.objects.create(
            title='Первая тестовая группа',
            slug='test-slug',
            description='Тестовое описание первой группы',
        )
        cls.group_for_add_group = Group.objects.create(
            title='Вторая тестовая группа',
            slug='test-slug-2',
            description='Тестовое описание второй группы',
        )
        for iteration in range(11):
            Post.objects.create(
                author=cls.user,
                text=f'Тестовый пост {iteration}',
                group=cls.group_for_paginator,
            )
        cls.post = Post.objects.create(
            author=cls.user_for_second_auth,
            text='Тестовый пост второй группы',
            group=cls.group_for_add_group,
        )
        cls.index = 'posts:index'
        cls.page_obj = 'page_obj'
        cls.group_list = 'posts:group_list'
        cls.profile = 'posts:profile'
        cls.post_detail = 'posts:post_detail'
        cls.post_edit = 'posts:post_edit'
        cls.create_post = 'posts:create_post'
        cache.clear()

    def tearDown(self):
        cache.clear()

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(PostsPagesContextTests.user)

    def test_posts_index_show_correct_context(self):
        """Тестирование корректного получения контекста в index."""
        post_count = Post.objects.count()

        response_page_one = self.authorized_client.get(reverse(self.index))
        response_page_two = self.authorized_client.get(reverse(self.index)
                                                       + '?page=2')
        len_response = (len(response_page_one.context.get(self.page_obj))
                        + len(response_page_two.context.get(self.page_obj)))

        self.assertEqual(len_response, post_count,
                         'Список постов передаваемый в index'
                         'не соответсвует ожидаемому')

    def test_posts_group_list_show_correct_context(self):
        """Тестирование корректного получения контекста в posts_group."""
        post_count = Post.objects.filter(
            group=self.group_for_add_group).count()
        group = self.group_for_add_group

        response = self.authorized_client.get(
            reverse(
                self.group_list,
                kwargs={'slug': self.group_for_add_group.slug}
            )
        )

        self.assertEqual(response.context.get('group'), group)
        self.assertEqual(len(response.context.get(self.page_obj)), post_count,
                         'Список постов передаваемый в group_list'
                         'не соответсвует ожидаемому')

    def test_posts_profile_show_correct_context(self):
        """Тестирование корректного получения контекста в profile."""
        post_count = Post.objects.filter(
            author=self.user_for_second_auth).count()
        author = self.user_for_second_auth

        response = self.authorized_client.get(
            reverse(
                self.profile,
                kwargs={'username': self.user_for_second_auth.username}
            )
        )

        self.assertEqual(response.context.get('author'), author)
        self.assertEqual(len(response.context.get(self.page_obj)), post_count,
                         'Список постов передаваемый в profile'
                         'не соответсвует ожидаемому')

    def test_posts_post_detail_show_correct_context(self):
        """Тестирование корректного получения контекста в post_detail."""
        post = Post.objects.get(pk=1)
        post_count = Post.objects.filter(author=self.user).count()

        response = self.authorized_client.get(reverse(
            self.post_detail, kwargs={'post_id': post.id}
        ))

        self.assertEqual(response.context.get('post_count'), post_count)
        self.assertEqual(response.context.get('post'), (post),
                         'Пост передаваемый в post_detail'
                         'не соответсвует ожидаемому')

    def test_posts_edit_post_show_correct_context(self):
        """Тестирование корректного получения контекста в post_edit."""
        response = self.authorized_client.get(
            reverse(self.post_edit, kwargs={'post_id': '1'})
        )
        is_edit = True

        self.assertEqual(response.context.get('is_edit'), is_edit)
        self.assertIsInstance(response.context.get('form'), PostForm)

    def test_posts_create_post_show_correct_context(self):
        """Тестирование корректного получения контекста в post_create."""
        response = self.authorized_client.get(reverse(self.create_post))

        self.assertIsInstance(response.context.get('form'), PostForm)

    def test_first_page_contains_ten_records(self):
        """Проверка отображения постов на первой странице."""
        field_verboses = (
            reverse(self.index),
            reverse(
                self.group_list,
                kwargs={'slug': self.group_for_paginator.slug}
            ),
            reverse(self.profile, kwargs={'username': self.user.username}),
        )

        for field in field_verboses:
            with self.subTest(field=field):
                response = self.client.get(field)
                self.assertEqual(
                    len(response.context[self.page_obj]),
                    settings.POSTS_PER_PAGE
                )

    def test_second_page_contains_three_records(self):
        """Проверка отображения постов на второй странице."""
        field_verboses = {
            reverse(self.index): 2,
            reverse(
                self.group_list,
                kwargs={'slug': self.group_for_paginator.slug}
            ): 1,
            reverse(self.profile, kwargs={'username': self.user.username}): 1,
        }

        for field, value in field_verboses.items():
            with self.subTest(field=field):
                response = self.client.get(field + '?page=2')
                self.assertEqual(len(response.context[self.page_obj]), value)

    def test_adding_new_post_on_index(self):
        """
        Тестирование передачи контекста нового поста
        с группой на страницу index.
        """
        post_count_index = Post.objects.count()
        Post.objects.create(
            author=self.user_for_second_auth,
            text='Добавочный тестовый пост второй группы',
            group=self.group_for_add_group,
        )

        response_list_page_one = self.authorized_client.get(
            reverse(self.index)
        )
        response_list_page_two = self.authorized_client.get(
            reverse(self.index) + '?page=2'
        )
        len_response_list = (
            (len(response_list_page_one.context.get(self.page_obj)))
            + (len(response_list_page_two.context.get(self.page_obj)))
        )

        self.assertEqual(len_response_list, post_count_index + 1)

    def test_adding_new_post_on_group_list(self):
        """
        Тестирование передачи контекста нового поста
        с группой на страницу group_list.
        """
        post_count_grop_list = Post.objects.filter(
            group=self.group_for_add_group).count()
        post = Post.objects.create(
            author=self.user_for_second_auth,
            text='Добавочный тестовый пост второй группы',
            group=self.group_for_add_group,
        )

        response_group_list = self.authorized_client.get(
            reverse(
                self.group_list,
                kwargs={'slug': self.group_for_add_group.slug}
            )
        )

        self.assertIn(
            response_group_list.context.get('group').title,
            post.group.title
        )
        self.assertEqual(len(response_group_list.context.get(self.page_obj)),
                         post_count_grop_list + 1)

    def test_adding_new_post_on_grop_list_ather(self):
        """
        Проверка на то, чтобы контекст нового поста
        с группой не попал в другую группу.
        """
        post = Post.objects.create(
            author=self.user_for_second_auth,
            text='Добавочный тестовый пост второй группы',
            group=self.group_for_add_group,
        )

        response = self.authorized_client.get(
            reverse(
                self.group_list,
                kwargs={'slug': self.group_for_paginator.slug})
        )

        self.assertNotIn(
            response.context.get('group').title,
            post.group.title
        )

    def test_adding_new_post_show_correct_context_on_profile(self):
        """
        Тестирование передачи контекста нового поста
        с группой на страницу profile автора.
        """
        post_count_profile = Post.objects.filter(
            author=self.user_for_second_auth).count()
        Post.objects.create(
            author=self.user_for_second_auth,
            text='Добавочный тестовый пост второй группы',
            group=self.group_for_add_group,
        )

        response_profile = self.authorized_client.get(
            reverse(
                self.profile,
                kwargs={'username': self.user_for_second_auth.username}
            )
        )

        self.assertEqual(len(response_profile.context.get(self.page_obj)),
                         post_count_profile + 1)

    def test_follow_unfollow_author(self):
        """
        Тестирование возможности
        подписаться/отписаться на/от автора.
        """
        response_follow = self.authorized_client.post(
            reverse('posts:profile_follow',
                    kwargs={'username': self.user_for_second_auth.username}),
        )
        response_after_follow = self.authorized_client.get(
            reverse('posts:follow_index',),
        )
        response_unfollow = self.authorized_client.post(
            reverse('posts:profile_unfollow',
                    kwargs={'username': self.user_for_second_auth.username}),
        )
        response_after_unfollow = self.authorized_client.get(
            reverse('posts:follow_index',),
        )

        self.assertTrue(
            response_after_follow.context.get(self.page_obj),
        )
        self.assertRedirects(
            response_follow,
            reverse('posts:follow_index')
        )
        self.assertFalse(
            response_after_unfollow.context.get(self.page_obj),
        )
        self.assertRedirects(
            response_unfollow,
            reverse('posts:follow_index')
        )

    def test_correct_context_after_follow_author(self):
        """
        Новая запись пользователя появляется в ленте тех,
        кто на него подписан и не появляется в ленте тех, кто не подписан.
        """
        self.authorized_second_client = Client()
        self.authorized_second_client.force_login(
            PostsPagesContextTests.user_for_second_auth
        )
        Post.objects.create(
            author=self.user_for_second_auth,
            text='Тестовый пост',
        )

        response_follow_first = self.authorized_client.post(
            reverse('posts:profile_follow',
                    kwargs={'username': self.user_for_second_auth.username}),
        )
        response_after_follow = self.authorized_client.get(
            reverse('posts:follow_index',),
        )
        response_unfollow_user = self.authorized_second_client.get(
            reverse('posts:follow_index',),
        )
        self.assertEqual(
            [*response_after_follow.context.get(self.page_obj)],
            [*Post.objects.filter(author=self.user_for_second_auth)]
        )
        self.assertRedirects(
            response_follow_first,
            reverse('posts:follow_index')
        )
        self.assertFalse(
            response_unfollow_user.context.get(self.page_obj),
        )


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsPagesImgContextTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
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
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group,
            image=uploaded,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()

    def test_img_on_index_show_correct_context(self):
        """
        Тестирование передачи контекста поста
        с картинкой на страницу image автора.
        """
        response = self.guest_client.get(reverse('posts:index'))

        self.assertIsNotNone(
            response.context.get('page_obj')[self.post.pk - 1].image
        )

    def test_img_on_group_list_show_correct_context(self):
        """
        Тестирование передачи контекста поста
        с картинкой на страницу group_list автора.
        """
        response = self.guest_client.get(reverse(
            'posts:group_list',
            kwargs={'slug': self.group.slug}
        ))

        self.assertIsNotNone(
            response.context.get('page_obj')[self.post.pk - 1].image
        )

    def test_img_on_profile_show_correct_context(self):
        """
        Тестирование передачи контекста поста
        с картинкой на страницу profile автора.
        """
        response = self.guest_client.get(reverse(
            'posts:profile',
            kwargs={'username': self.user.username}
        ))

        self.assertIsNotNone(
            response.context.get('page_obj')[self.post.pk - 1].image
        )

    def test_img_on_post_detail_show_correct_context(self):
        """
        Тестирование передачи контекста поста
        с картинкой на страницу post_detail автора.
        """
        response = self.guest_client.get(reverse(
            'posts:post_detail',
            kwargs={'post_id': self.post.pk}
        ))

        self.assertIsNotNone(response.context.get('post').image)
