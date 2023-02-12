from django import forms
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from django.conf import settings

from ..models import Group, Post

User = get_user_model()


class PostViewTests(TestCase):
    """Создаем тестовых юзера, пост и группу."""
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(
            username='author'
        )
        cls.group = Group.objects.create(
            title='Тестовое название группы',
            description='Тестовое описание группы',
            slug='test-slug',
        )
        cls.post = Post.objects.create(
            text='Тестовый пост',
            group=cls.group,
            author=cls.user
        )

    def setUp(self):
        """Создание клиентов гостя и зарегистрированного пользователя."""
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_use_correct_template(self):
        """View-функции используют соответствующие шаблоны."""
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list', kwargs=(
                {'slug': f'{self.post.group.slug}'})): 'posts/group_list.html',
            reverse('posts:profile', kwargs=(
                {'username': f'{self.user}'})): 'posts/profile.html',
            reverse('posts:post_detail', kwargs=(
                {'post_id': f'{self.post.id}'})): 'posts/post_detail.html',
            reverse('posts:post_edit', kwargs=(
                {'post_id': f'{self.post.id}'})): 'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html',
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def check_post(self, response_context):
        if 'page_obj' in response_context:
            post = response_context['page_obj'][0]
        else:
            post = response_context['post']
        self.assertEqual(post.text, self.post.text)
        self.assertEqual(post.group, self.post.group)
        self.assertEqual(post.author, self.post.author)

    def post_create_edit(self, response_context):
        form_field = [
            ('text', forms.fields.CharField),
            ('group', forms.fields.ChoiceField),
        ]
        for value, excepted in form_field:
            with self.subTest(value=value):
                form_field = response_context.get('form').fields.get(value)
                self.assertIsInstance(form_field, excepted)

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        self.check_post(response.context)

    def test_post_detail_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.pk})
        )
        self.check_post(response.context)

    def test_group_list_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': self.group.slug})
        )
        self.check_post(response.context)
        self.assertEqual(response.context['group'], self.group)

    def test_profile_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': self.post.author})
        )
        self.check_post(response.context)
        self.assertEqual(response.context['author'], self.user)

    def test_post_edit_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': self.post.pk})
        )
        self.post_create_edit(response.context)

    def test_post_create_show_correct_context(self):
        """Шаблон create_post сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        self.post_create_edit(response.context)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='author')
        cls.authorized_author = Client()
        cls.authorized_author.force_login(cls.author)

    AMOUNT_OF_TEST_POSTS = settings.POSTS_PER_PAGE + 3

    def setUp(self):
        self.group = Group.objects.create(
            title='Тестовое название',
            description='Тестовое описание',
            slug='test-slug',
        )
        self.post = Post.objects.bulk_create([
            Post(author=self.author,
                 text=f'Тестовый пост {i}',
                 group=self.group) for i in range(self.AMOUNT_OF_TEST_POSTS)]
        )
        self.page_names_records = {
            'posts:index': '',
            'posts:profile': {'username': self.author.username},
            'posts:group_list': {'slug': self.group.slug},
        }

    def test_first_page_has_ten_posts(self):
        """На первой странице с паджинатором верное количество постов."""
        for page_name, kwarg in self.page_names_records.items():
            with self.subTest(page_name=page_name):
                response = self.client.get(reverse(page_name, kwargs=kwarg))
                self.assertEqual(
                    len(response.context['page_obj']), settings.POSTS_PER_PAGE)

    def test_second_page_has_three_posts(self):
        """На второй странице с паджинатором верное количество постов."""
        POSTS_ON_SECOND_PAGE = (
            self.AMOUNT_OF_TEST_POSTS - settings.POSTS_PER_PAGE
        )
        for page_name, kwarg in self.page_names_records.items():
            with self.subTest(page_name=page_name):
                response = self.client.get(reverse(
                    page_name, kwargs=kwarg) + '?page=2')
                self.assertEqual(
                    len(response.context['page_obj']), POSTS_ON_SECOND_PAGE)
