from celery import shared_task

from scripts.bots import (
    BaseCrawler,
    CNNCrawler,
    G1Crawler,
    MetropolesCrawler,
    UOLCrawler,
)
from scripts.logger import logger
from scripts.services import VectorDatabase


@shared_task
def buscar_noticias():
    vector_database = VectorDatabase()
    crawlers: list[BaseCrawler] = [
        CNNCrawler(logger, vector_database),
        G1Crawler(logger, vector_database),
        MetropolesCrawler(logger, vector_database),
        UOLCrawler(logger, vector_database),
    ]

    for crawler in crawlers:
        crawler.crawl()
