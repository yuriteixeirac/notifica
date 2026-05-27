import feedparser
import requests
from bs4 import BeautifulSoup
from feedparser.api import FeedParserDict

from scripts.bots import BaseCrawler


class UOLCrawler(BaseCrawler):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.rss_url = "https://rss.home.uol.com.br/index.xml"

    def crawl(self) -> None:
        feed = feedparser.parse(self.rss_url)
        if feed.status != 200:
            raise requests.exceptions.HTTPError()

        token = self._get_token()

        for entry in feed.entries:
            if entry is None:
                continue

            url: str = entry.link  # type: ignore
            if self._is_repetida(url):
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

    def _get_imagem(self, source: str | FeedParserDict) -> str | None:
        content = requests.get(source)  # type: ignore
        if content.status_code != 200:
            return
        soup = BeautifulSoup(content.text, "html.parser")  # type: ignore
        imagem = soup.find("img")
        if not imagem:
            return
        return imagem.attrs.get("src", None)  # type: ignore

    def _get_title(self, url: str) -> str | None:
        html = requests.get(url).text
        soup = BeautifulSoup(html, "html.parser")

        title = soup.select_one("h1.title")
        if not title:
            return None

        return title.text

    def _montar_noticia(self, noticia: FeedParserDict) -> dict:
        return {
            "titulo": self._get_title(noticia.link),  # type: ignore
            "sumario": noticia.summary,
            "link": noticia.link,
            "imagem": self._get_imagem(noticia.link),  # type: ignore
            "disponivel": True,
        }
