import os
from abc import ABC, abstractmethod

import requests
from feedparser.api import FeedParserDict
from newspaper import Article

from scripts.services.vector_database import VectorDatabase


class BaseCrawler(ABC):
    def __init__(self, logger, vector_db: VectorDatabase) -> None:
        self.api_url = os.getenv("API_URL")
        self.vector_db = vector_db
        self.content: str | None = None
        self.logger = logger

    def _get_token(self) -> str:
        response = requests.post(
            f"{self.api_url}/login/",
            json={
                "username": os.getenv("SUPER_USER_USERNAME"),
                "password": os.getenv("SUPER_USER_PASSWORD"),
            },
        )

        body = response.json()
        token = body.get("access")

        return token

    @abstractmethod
    def _montar_noticia(self, noticia: FeedParserDict) -> dict:
        pass

    @abstractmethod
    def _get_imagem(self, source: str | FeedParserDict) -> str | None:
        pass

    @abstractmethod
    def crawl(self) -> None:
        pass

    def _is_repetida(self, url: str) -> bool:
        conteudo = self._get_artigo(url)
        similaridade = self.vector_db.get_maior_similaridade(conteudo)

        if similaridade > 0.80:
            return True
        return False

    def _indexa_noticia(self, url: str) -> None:
        conteudo = self._get_artigo(url)
        self.vector_db.inserir_noticia(conteudo)

    def _get_artigo(self, url: str) -> str:
        article = Article(url, language="pt")
        article.download()
        article.parse()

        return article.text
