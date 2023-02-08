from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from ..models import Group, Post


User = get_user_model()


class PostFormsTest(TestCase):
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
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Текст нового тестового поста',
            'group': self.group.pk,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )
        new_post = Post.objects.first()
        self.assertRedirects(response, reverse(
            'posts:profile', kwargs={'username': self.user.username})
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertEqual(new_post.group, self.group)
        self.assertEqual(new_post.author, self.user)
        self.assertEqual(new_post.text, form_data['text'])

    def test_edit_post(self):
        """Валидная форма редактирует запись в Post."""
        form_data = {
            'text': 'Текст нового тестового поста, редактируем...',
            'group': self.group.pk,
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.pk}),
            data=form_data,
            follow=True,
        )
        post = Post.objects.get(pk=self.post.pk)
        self.assertRedirects(response, reverse(
            'posts:post_detail', kwargs={'post_id': self.post.pk})
        )
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.group.pk, form_data['group'])
