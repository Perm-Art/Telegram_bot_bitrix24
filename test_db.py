from database.db_manager import DatabaseManager

db = DatabaseManager()
user = db.get_or_create_user("123456", "test_user")
print(f"Created user: {user}")
