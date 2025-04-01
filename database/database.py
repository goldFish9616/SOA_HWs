from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import declarative_base, sessionmaker
import os

# Получаем URL базы данных из переменных окружения
DATABASE_URL = os.getenv("DATABASE_URL")

# Разделяем URL и схему (по умолчанию схема public)
if "?schema=" in DATABASE_URL:
    DATABASE_URL, schema = DATABASE_URL.split("?schema=")
else:
    schema = "public"

print("✅ Подключение к БД:", DATABASE_URL)


# Подключение к базе данных
engine = create_engine(DATABASE_URL)

# Создание сессии
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Указываем схему в MetaData
metadata = MetaData(schema=schema)
Base = declarative_base(metadata=metadata)

print("✅ Создание таблиц...")
Base.metadata.create_all(engine)
print("✅ Таблицы созданы!")


# Функция получения сессии БД
def get_db():
    db = SessionLocal()
    db.execute(f"SET search_path TO {schema};")  # Устанавливаем схему для текущей сессии
    try:
        yield db
    finally:
        db.close()
