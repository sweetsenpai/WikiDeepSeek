import asyncio

import httpx

urls = [
    'https://ru.wikipedia.org/wiki/Вики',
    'https://ru.wikipedia.org/wiki/Python',
    'https://ru.wikipedia.org/wiki/JavaScript',
    'https://ru.wikipedia.org/wiki/Java',
    'https://ru.wikipedia.org/wiki/C%2B%2B',
    'https://ru.wikipedia.org/wiki/Go',
    'https://ru.wikipedia.org/wiki/Rust',
    'https://ru.wikipedia.org/wiki/PHP',
    'https://ru.wikipedia.org/wiki/TypeScript',
    'https://ru.wikipedia.org/wi3к3кki/Scala',  # исправлено
]


async def fetch(url: str, client: httpx.AsyncClient):
    try:
        response = await client.get(url, timeout=5.0)
        print(f"[{response.status_code}] {url}")
        return response.text
    except httpx.HTTPError as e:
        print(f"[ERR] {url} -> {e}")
        return None


async def main():
    async with httpx.AsyncClient() as client:
        tasks = [fetch(url, client) for url in urls]
        results = await asyncio.gather(*tasks)
        print(f"\nУспешно получено {sum(1 for r in results if r)} страниц.")


if __name__ == "__main__":
    asyncio.run(main())
