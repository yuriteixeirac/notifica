from rest_framework import serializers

from apps.postagens.models import Postagem


class PostagemInputSerializer(serializers.Serializer):
    titulo = serializers.CharField()
    corpo = serializers.CharField()
    disponivel = serializers.BooleanField(required=False)

    def create(self, validated_data):
        return Postagem.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.titulo = validated_data.get('titulo', instance.titulo)
        instance.corpo = validated_data.get('corpo', instance.corpo)
        instance.disponivel = validated_data.get('disponivel', instance.disponivel)
        instance.save()

        return instance
