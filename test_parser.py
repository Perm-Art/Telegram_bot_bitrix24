# test_parser.py
import asyncio
from parser.bitrix_parser import BitrixParser

async def test():
    parser = BitrixParser()
    docs = await parser.parse_documentation(max_pages=5)
    for doc in docs:
        print(f"Title: {doc['title']}")
        print(f"URL: {doc['url']}")
        print(f"Content length: {len(doc['content'])}")
        print("---")

asyncio.run(test())