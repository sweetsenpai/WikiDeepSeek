import asyncio
import time

import httpx
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)
from wiki_parser import ArticleParser

MAX_LEVEL = 2
CONCURRENT_WORKERS = 20
START_URL = 'https://ru.wikipedia.org/wiki/Python'

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
        if parced_page:
            processed.add(url)
        else:
            failed.add(url)
        print(
            f"✅ Успешно: {url}\n{parced_page.get('title')}\nlevel:{article.level}\nСвязанных ссылок:{len(article.article_related_urls)}\n--------------------"
        )
        print(f"Всего обработанно ссылок:{len(processed)}")
        if article.level < MAX_LEVEL:
            for new_url in article.article_related_urls:
                if new_url not in processed and new_url not in failed:
                    print(
                        f"Добавляю в очередь: {new_url}, текущий размер: {queue.qsize()}"
                    )
                    await queue.put((new_url, article.level + 1))
                    print(f"Добавил в очередь: {new_url}")

    except Exception as e:
        print(f"❌ Ошибка на {url}: {e}")
        failed.add(url)


async def worker(queue: asyncio.Queue, client: httpx.AsyncClient):
    while True:
        url, level = await queue.get()
        await asyncio.wait_for(fetch_and_parse(url, client, queue, level), 5)
        queue.task_done()


async def main():

    start_time = time.time()
    queue = asyncio.Queue()
    await queue.put((START_URL, 0))
    limits = httpx.Limits(max_connections=500, max_keepalive_connections=50)
    timeout = httpx.Timeout(5.0, connect=3.0)

    async with httpx.AsyncClient(limits=limits, timeout=timeout) as client:
        tasks = []
        for i in range(CONCURRENT_WORKERS):
            task = asyncio.create_task(worker(queue, client))
            tasks.append(task)

        await queue.join()
        for task in tasks:
            task.cancel()
    end_time = time.time()
    execution_time = end_time - start_time
    print(f"Всего обработанно ссылок:{len(processed)}")
    print(f"Всего не валидных ссылок:{len(failed)}")
    print(f"Время выполнения: {execution_time:.4f} секунд")


if __name__ == "__main__":
    asyncio.run(main())
