from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse

from http import HTTPStatus

from ..models import Post, Group


User = get_user_model()


class PostURLTests(TestCase):
    """Создание тестового поста и группы."""
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(
            username="test_user"
        )
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_group',
            description='Тестовое описание тестовой группы'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый тест тестового поста без группы'
        )

    def setUp(self):
        """Создание клиентов гостя и зарегистрированного пользователя."""
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_urls_response_for_guest(self):
        """Проверка статуса страниц для гостевого аккаунта."""
        url_status = {
            reverse('posts:index'): HTTPStatus.OK,
            reverse('posts:group_list', kwargs={
                'slug': PostURLTests.group.slug}): HTTPStatus.OK,
            reverse('posts:profile', kwargs={
                'username': PostURLTests.user.username}): HTTPStatus.OK,
            reverse('posts:post_detail', kwargs={
                'post_id': PostURLTests.post.pk}): HTTPStatus.OK,
            reverse('posts:post_edit', kwargs={
                'post_id': PostURLTests.post.pk}): HTTPStatus.FOUND,
            reverse('posts:post_create'): HTTPStatus.FOUND,
            '/unexisting_page/': HTTPStatus.NOT_FOUND,
        }
        for url, status_code in url_status.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, status_code)

    def test_urls_response_for_authenticated_user(self):
        """Проверка статуса страниц для авторизованного пользователя."""
        url_status = {
            reverse('posts:index'): HTTPStatus.OK,
            reverse('posts:group_list', kwargs={
                'slug': PostURLTests.group.slug}): HTTPStatus.OK,
            reverse('posts:profile', kwargs={
                'username': PostURLTests.user.username}): HTTPStatus.OK,
            reverse('posts:post_detail', kwargs={
                'post_id': PostURLTests.post.pk}): HTTPStatus.OK,
            reverse('posts:post_edit', kwargs={
                'post_id': '1'}): HTTPStatus.FOUND,
            reverse('posts:post_edit', kwargs={
                'post_id': PostURLTests.post.pk}): HTTPStatus.OK,
            reverse('posts:post_create'): HTTPStatus.OK,
            '/unexisting_page/': HTTPStatus.NOT_FOUND,
        }
        for url, status_code in url_status.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertEqual(response.status_code, status_code)
