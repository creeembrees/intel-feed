from dotenv import load_dotenv
import os

load_dotenv()

print("HOST:", os.getenv("DB_HOST"))
print("NAME:", os.getenv("DB_NAME"))
print("USER:", os.getenv("DB_USER"))
print("PASSWORD:", os.getenv("DB_PASSWORD"))
print("PORT:", os.getenv("DB_PORT"))
