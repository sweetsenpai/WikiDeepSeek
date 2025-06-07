import asyncio
import logging
import os
import time

import httpx
import redis.asyncio as redis
from dotenv import load_dotenv
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from app.configs.redis_config import get_redis

from .wiki_parser import ArticleParser

load_dotenv()
logger = logging.getLogger(__name__)

MAX_LEVEL = int(os.getenv("MAX_LEVEL"))
CONCURRENT_WORKERS = int(os.getenv("CONCURRENT_WORKERS"))

processed = set()
in_work = {}
failed = set()


@retry(
    stop=stop_after_attempt(2),
    wait=wait_exponential(multiplier=1, max=2),
    retry=retry_if_exception_type(
        (httpx.ConnectError, httpx.HTTPError, httpx.ReadError, httpx.TimeoutException)
    ),
)
async def fetch_and_parse(
    url: str, client: httpx.AsyncClient, queue: asyncio.Queue, level: int = 0
):
    try:
        in_work[url] = True
        response = await client.get(url)
        response.raise_for_status()
        article = ArticleParser(response.text, url, level=level)
        parced_page = await asyncio.to_thread(article.article_collect_data)
        del in_work[url]
        if not parced_page:
            await redis.sadd.add("failed", url)

        logger.debug(
            f"✅ Успешно: {url}\n{parced_page.get('title')}\nlevel:{article.level}\nСвязанных ссылок:{len(article.article_related_urls)}\n--------------------"
        )
        logger.debug(
            f"Всего обработанно ссылок:{len(await redis.smembers('processed'))}"
        )
        if article.level < MAX_LEVEL:
            await redis.sadd.add("processed", url)
            for new_url in article.article_related_urls:
                if not await redis_client.sismember(
                    "processed", url
                ) and not await redis_client.sismember("failed", url):
                    await queue.put((new_url, article.level + 1))

    except Exception as e:
        logger.warning(f"❌ Ошибка на {url}: {e}")
        await redis.sadd.add("failed", url)


async def worker(queue: asyncio.Queue, client: httpx.AsyncClient, redis):
    while True:
        url, level = await queue.get()
        await asyncio.wait_for(fetch_and_parse(url, client, queue, level, redis), 5)
        queue.task_done()


async def run_parser(start_url: str = 'https://ru.wikipedia.org/wiki/Python'):
    redis = get_redis()
    queue = asyncio.Queue()
    await queue.put((start_url, 0))
    limits = httpx.Limits(max_connections=500, max_keepalive_connections=50)
    timeout = httpx.Timeout(5.0, connect=3.0)

    async with httpx.AsyncClient(limits=limits, timeout=timeout) as client:
        tasks = []
        for i in range(CONCURRENT_WORKERS):
            task = asyncio.create_task(worker(queue, client, redis))
            tasks.append(task)

        await queue.join()

        for task in tasks:
            task.cancel()
