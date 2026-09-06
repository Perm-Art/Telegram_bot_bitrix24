"""База знаний по Bitrix24 API"""

BITRIX24_KNOWLEDGE = {
    "crm": {
        "deals": {
            "methods": ["crm.deal.list", "crm.deal.get", "crm.deal.add", "crm.deal.update", "crm.deal.delete"],
            "description": "Работа со сделками в CRM",
            "example": "GET /rest/crm.deal.list"
        },
        "leads": {
            "methods": ["crm.lead.list", "crm.lead.get", "crm.lead.add", "crm.lead.update"],
            "description": "Работа с лидами в CRM",
            "example": "POST /rest/crm.lead.add"
        },
        "contacts": {
            "methods": ["crm.contact.list", "crm.contact.get", "crm.contact.add"],
            "description": "Работа с контактами в CRM",
            "example": "GET /rest/crm.contact.list"
        }
    },
    "auth": {
        "webhook": {
            "description": "Простая авторизация через вебхук",
            "example": "https://your-portal.bitrix24.ru/rest/1/token/"
        },
        "oauth": {
            "description": "OAuth 2.0 авторизация",
            "example": "https://oauth.bitrix.info/oauth/token/"
        }
    }
}

def get_knowledge_context(query: str) -> str:
    """Получение контекста из базы знаний"""
    query_lower = query.lower()
    context_parts = []
    
    # Поиск по ключевым словам
    if "сделк" in query_lower or "deal" in query_lower:
        context_parts.append("Методы для работы со сделками: crm.deal.list, crm.deal.get, crm.deal.add")
    
    if "лид" in query_lower or "lead" in query_lower:
        context_parts.append("Методы для работы с лидами: crm.lead.list, crm.lead.get, crm.lead.add")
    
    if "контакт" in query_lower or "contact" in query_lower:
        context_parts.append("Методы для работы с контактами: crm.contact.list, crm.contact.get, crm.contact.add")
    
    if "вебхук" in query_lower or "webhook" in query_lower:
        context_parts.append("Вебхук: https://your-portal.bitrix24.ru/rest/1/token/")
    
    return "\n".join(context_parts) if context_parts else ""
