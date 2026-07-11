from django.core.files.base import File
from django.core.files.images import ImageFile
from django.core.files.uploadedfile import UploadedFile
from rest_framework import serializers

from apps.noticias.services import upload_image
from apps.postagens.models import Postagem


class ImageFileOuUrl(serializers.Field):
    def to_internal_value(self, data):
        if isinstance(data, (File, ImageFile, UploadedFile)):
            try:
                return upload_image(data).url
            except Exception as exc:
                raise serializers.ValidationError(
                    "Não foi possível enviar a imagem."
                ) from exc

        if isinstance(data, str):
            return serializers.URLField().run_validation(data)

        raise serializers.ValidationError(
            "Campo 'imagem' deve ser uma URL ou arquivo de imagem."
        )

    def to_representation(self, value) -> str:
        return str(value)


class PostagemInputSerializer(serializers.Serializer):
    titulo = serializers.CharField()
    corpo = serializers.CharField()
    cor_fundo = serializers.RegexField(
        regex=r'^#(?:[0-9a-fA-F]{3}){1,2}$',
        required=False,
        allow_null=True,
        max_length=7,
        error_messages={
            'invalid': "Campo 'cor_fundo' deve ser uma cor hexadecimal válida."
        },
    )
    imagem = ImageFileOuUrl(required=False, allow_null=True)
    disponivel = serializers.BooleanField(required=False)

    def validate(self, attrs):
        if attrs.get('cor_fundo') and attrs.get('imagem'):
            raise serializers.ValidationError(
                "Informe apenas 'cor_fundo' ou 'imagem', não ambos."
            )

        return attrs

    def create(self, validated_data):
        return Postagem.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.titulo = validated_data.get('titulo', instance.titulo)
        instance.corpo = validated_data.get('corpo', instance.corpo)

        if 'cor_fundo' in validated_data:
            instance.cor_fundo = validated_data.get('cor_fundo')

            if instance.cor_fundo:
                instance.imagem = None

        if 'imagem' in validated_data:
            instance.imagem = validated_data.get('imagem')

            if instance.imagem:
                instance.cor_fundo = None

        instance.disponivel = validated_data.get('disponivel', instance.disponivel)
        instance.save()

        return instance
