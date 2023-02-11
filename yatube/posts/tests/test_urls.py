from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()


class PostURLTests(TestCase):
    """Создание тестового поста и группы."""
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.authorized_user = User.objects.create_user(
            username="test_authorized_user"
        )
        cls.authorized_user_author = User.objects.create_user(
            username="test_authorized_author"
        )
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_group',
            description='Тестовое описание тестовой группы'
        )
        cls.post = Post.objects.create(
            author=cls.authorized_user_author,
            text='Тестовый тест тестового поста без группы'
        )

    def setUp(self):
        """Создание клиентов гостя и зарегистрированного пользователя."""
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.authorized_user)
        self.authorized_author = Client()
        self.authorized_author.force_login(self.authorized_user_author)

    def test_all_urls(self):
        """Тест статусов для всех видов пользователей.
        Пользователи: гость, авторизованный без постов и автор поста."""
        urls_list = [
            ('', self.guest_client, HTTPStatus.OK),
            ('', self.authorized_client, HTTPStatus.OK),
            ('', self.authorized_author, HTTPStatus.OK),

            ('group/test_group/', self.guest_client, HTTPStatus.OK),
            ('group/test_group/', self.authorized_client, HTTPStatus.OK),
            ('group/test_group/', self.authorized_author, HTTPStatus.OK),
            
            ('profile/test_user', self.guest_client, HTTPStatus.OK),
            ('profile/test_user', self.authorized_client, HTTPStatus.OK),
            ('profile/test_user', self.authorized_author, HTTPStatus.OK),

            (f'posts/{self.post.pk}/', self.guest_client, HTTPStatus.OK),
            (f'posts/{self.post.pk}/', self.authorized_client, HTTPStatus.OK),
            (f'posts/{self.post.pk}/', self.authorized_author, HTTPStatus.OK),

            ('create/', self.guest_client, HTTPStatus.FOUND),
            ('create/', self.authorized_client, HTTPStatus.OK),
            ('create/', self.authorized_author, HTTPStatus.OK),

            (f'posts/{self.post.pk}/edit/', self.guest_client, HTTPStatus.FOUND),
            (f'posts/{self.post.pk}/edit/', self.authorized_client, HTTPStatus.FOUND),
            (f'posts/{self.post.pk}/edit/', self.authorized_author, HTTPStatus.OK),

            ('/unexisting_page/', self.guest_client, HTTPStatus.NOT_FOUND),
            ('/unexisting_page/', self.authorized_client, HTTPStatus.NOT_FOUND),
            ('/unexisting_page/', self.authorized_author, HTTPStatus.NOT_FOUND),
        ]
        for url, client, status_code in urls_list:
            with self.subTest(url=url):
                response = client.get(url)
                self.assertEqual(response.status_code, status_code)
