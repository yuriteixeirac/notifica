import feedparser
import requests
from bs4 import BeautifulSoup
from feedparser.api import FeedParserDict

from scripts.bots import BaseCrawler


class MetropolesCrawler(BaseCrawler):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.rss_url = "https://metropoleonline.com.br/rss/latest-posts"

    def crawl(self) -> None:
        feed = feedparser.parse(self.rss_url)
        if feed.status != 200:
            raise requests.exceptions.HTTPError()

        token = self._get_token()

        for entry in feed.entries:
            url: str = entry.link  # type: ignore
            if self._is_repetida(url):  # type: ignore
                self.logger.error(f"NOTÍCIA JÁ INDEXADA: {url}.")
                continue

            self._indexa_noticia(url)

            noticia = self._montar_noticia(entry)

            result = requests.post(
                f"{self.api_url}/noticia/",
                json=noticia,
                headers={"Authorization": f"Token {token}"},
            )

            if result.status_code != 201:
                self.logger.error(
                    f"STATUS CODE {result.status_code} PARA {entry.link}."
                )

    def _montar_noticia(self, noticia: FeedParserDict) -> dict[str, any]:  # type: ignore
        return {
            "titulo": noticia.title,
            "sumario": noticia.summary + ".",  # type: ignore
            "link": noticia.link,
            "imagem": self._get_imagem(noticia.link),  # type: ignore
        }

    def _get_imagem(self, source: str | FeedParserDict) -> str | None:  # type: ignore
        html = requests.get(source).text  # type: ignore
        soup = BeautifulSoup(html, "html.parser")

        imagem = soup.select_one("img.img-fluid.center-image")
        if not imagem:
            return
        return imagem.get("src")  # type: ignore
