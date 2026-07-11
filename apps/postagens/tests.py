from django.test import TestCase
from rest_framework.test import APIRequestFactory, force_authenticate

from apps.accounts.models import Usuario
from apps.postagens.models import Postagem
from apps.postagens.views import PostagemViewSet


class PostagemViewSetTests(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.usuario = Usuario.objects.create(
            username='usuario1',
            email='usuario1@example.com',
            nome='Usuario',
            sobrenome='Um',
            cargo=Usuario.Cargo.SERVIDOR,
        )
        self.outro_usuario = Usuario.objects.create(
            username='usuario2',
            email='usuario2@example.com',
            nome='Usuario',
            sobrenome='Dois',
            cargo=Usuario.Cargo.SERVIDOR,
        )
        self.postagem = Postagem.objects.create(
            titulo='Titulo original',
            corpo='Corpo original',
            usuario=self.usuario,
        )

    def test_update_atualiza_postagem_do_usuario(self):
        request = self.factory.put(f'/api/postagem/{self.postagem.pk}/', {
            'titulo': 'Titulo atualizado',
            'corpo': 'Corpo atualizado',
            'disponivel': False,
        }, format='json')
        force_authenticate(request, user=self.usuario)

        response = PostagemViewSet.as_view({'put': 'update'})(
            request,
            pk=self.postagem.pk,
        )

        self.assertEqual(response.status_code, 200)
        self.postagem.refresh_from_db()
        self.assertEqual(self.postagem.titulo, 'Titulo atualizado')
        self.assertEqual(self.postagem.corpo, 'Corpo atualizado')
        self.assertFalse(self.postagem.disponivel)

    def test_update_nao_atualiza_postagem_de_outro_usuario(self):
        request = self.factory.put(f'/api/postagem/{self.postagem.pk}/', {
            'titulo': 'Titulo indevido',
            'corpo': 'Corpo indevido',
            'disponivel': False,
        }, format='json')
        force_authenticate(request, user=self.outro_usuario)

        response = PostagemViewSet.as_view({'put': 'update'})(
            request,
            pk=self.postagem.pk,
        )

        self.assertEqual(response.status_code, 404)
        self.postagem.refresh_from_db()
        self.assertEqual(self.postagem.titulo, 'Titulo original')
        self.assertEqual(self.postagem.corpo, 'Corpo original')
        self.assertTrue(self.postagem.disponivel)

    def test_destroy_remove_postagem_do_usuario(self):
        request = self.factory.delete(f'/api/postagem/{self.postagem.pk}/')
        force_authenticate(request, user=self.usuario)

        response = PostagemViewSet.as_view({'delete': 'destroy'})(
            request,
            pk=self.postagem.pk,
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(Postagem.objects.filter(pk=self.postagem.pk).exists())

    def test_viewset_nao_implementa_patch(self):
        self.assertFalse(hasattr(PostagemViewSet, 'partial_update'))
