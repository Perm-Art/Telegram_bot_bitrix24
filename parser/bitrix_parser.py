# parser/bitrix_parser.py
import aiohttp
from bs4 import BeautifulSoup
from typing import List, Dict
import asyncio

class BitrixParser:
    def __init__(self):
        self.base_url = "https://apidocs.bitrix24.ru/"
        self.visited = set()
    
    async def parse_documentation(self, max_pages: int = 10) -> List[Dict]:
        """Парсинг документации"""
        documents = []
        start_urls = [
            "https://apidocs.bitrix24.ru/api-reference/",
            "https://apidocs.bitrix24.ru/rest-api/"
        ]
        
        for url in start_urls:
            docs = await self.parse_page(url)
            documents.extend(docs)
            
            if len(documents) >= max_pages:
                break
        
        return documents
    
    async def parse_page(self, url: str) -> List[Dict]:
        """Парсинг одной страницы"""
        if url in self.visited:
            return []
        
        self.visited.add(url)
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    return []
                
                html = await response.text()
                soup = BeautifulSoup(html, 'lxml')
                
                # Извлечение заголовка
                title = soup.find('h1')
                title_text = title.text if title else "Без заголовка"
                
                # Извлечение контента
                content_div = soup.find('div', class_='content')
                content_text = content_div.text if content_div else ""
                
                # Ограничение размера контента
                content_text = content_text[:5000]  # Ограничение
                
                return [{
                    'url': url,
                    'title': title_text,
                    'content': content_text,
                    'category': self.get_category(url)
                }]
    
    def get_category(self, url: str) -> str:
        """Определение категории"""
        if 'api-reference' in url:
            return 'api_reference'
        elif 'rest-api' in url:
            return 'rest_api'
        else:
            return 'general'