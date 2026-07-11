from rest_framework import serializers

from apps.accounts.serializers import UsuarioSerializer


class PostagemOutputSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=False)
    titulo = serializers.CharField()
    corpo = serializers.CharField()
    publicado_em = serializers.DateTimeField(required=False)
    disponivel = serializers.BooleanField()
    usuario = UsuarioSerializer(required=False)
