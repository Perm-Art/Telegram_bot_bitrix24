# yandex_assistant/assistant.py
import aiohttp
import json
from typing import List, Dict

class YandexGPT:
    def __init__(self, api_key: str, folder_id: str):
        self.api_key = api_key
        self.folder_id = folder_id
        self.base_url = "https://llm.api.cloud.yandex.net/foundationModels/v1"
    
    async def generate_response(self, prompt: str, context: str = "") -> str:
        messages = [
            {"role": "system", "text": "Вы эксперт по Bitrix24 API"},
            {"role": "user", "text": prompt}
        ]
        
        if context:
            messages.insert(1, {"role": "system", "text": f"Контекст: {context}"})
        
        request_body = {
            "modelUri": f"gpt://{self.folder_id}/yandexgpt/latest",
            "completionOptions": {
                "stream": False,
                "temperature": 0.3,
                "maxTokens": 2000
            },
            "messages": messages
        }
        
        headers = {
            "Authorization": f"Api-Key {self.api_key}",
            "Content-Type": "application/json"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/completion",
                json=request_body,
                headers=headers
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    return result['result']['alternatives'][0]['message']['text']
                else:
                    return f"Ошибка: {response.status}"