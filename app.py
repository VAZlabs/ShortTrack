from flask import Flask, request, jsonify, render_template
from sqlalchemy import create_engine, Column, String, Text, DateTime, ForeignKey
from sqlalchemy.dialects.sqlite import VARCHAR  # Используем типы данных для SQLite
from sqlalchemy.orm import sessionmaker, relationship, declarative_base
from sqlalchemy.sql import func
import uuid
import random
import string
from config import DATABASE_URL

# Создание объекта Flask
app = Flask(__name__)

# Создание подключения к базе данных SQLite
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})  # Для SQLite нужно указать connect_args

# Создание сессии
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Создание Base
Base = declarative_base()

# Модель для сокращённых ссылок
class ShortLink(Base):
    __tablename__ = "short_links"

    id = Column(VARCHAR(36), primary_key=True, default=str(uuid.uuid4))
    original_url = Column(Text, nullable=False)  # Оригинальная ссылка
    short_code = Column(VARCHAR(10), unique=True, nullable=False)  # Сокращённый код
    created_at = Column(DateTime, server_default=func.now())  # Дата создания
    expires_at = Column(DateTime, nullable=True)  # Дата истечения (если есть)

# Модель для хранения статистики кликов
class Click(Base):
    __tablename__ = "clicks"

    id = Column(VARCHAR(36), primary_key=True, default=str(uuid.uuid4))
    link_id = Column(VARCHAR(36), ForeignKey('short_links.id'), nullable=False)
    clicked_at = Column(DateTime, server_default=func.now())  # Время клика
    ip_address = Column(Text, nullable=True)  # IP адрес
    user_agent = Column(Text, nullable=True)  # Информация о браузере/устройстве
    referer = Column(Text, nullable=True)  # Источник перехода (реферер)

    # Связь с сокращённой ссылкой
    link = relationship("ShortLink", backref="clicks")

# Генерация случайного сокращённого кода
def generate_short_code(length=10):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

# Получение сессии для работы с БД
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Эндпоинт для создания сокращённой ссылки
@app.route("/shorten/", methods=["POST"])
def shorten_url():
    db = next(get_db())
    original_url = request.json.get("original_url")
    if not original_url:
        return jsonify({"error": "Original URL is required"}), 400
    
    short_code = generate_short_code()
    db_link = ShortLink(original_url=original_url, short_code=short_code)
    db.add(db_link)
    db.commit()
    db.refresh(db_link)
    return jsonify({"short_code": db_link.short_code, "original_url": db_link.original_url})

# Эндпоинт для статистики по кликам
@app.route("/stats/<short_code>", methods=["GET"])
def get_stats(short_code):
    db = next(get_db())
    db_link = db.query(ShortLink).filter(ShortLink.short_code == short_code).first()
    if db_link is None:
        return jsonify({"error": "Link not found"}), 404
    
    # Получаем количество кликов
    click_count = db.query(Click).filter(Click.link_id == db_link.id).count()

    # Отрисовываем страницу статистики
    return render_template("stats.html", short_code=short_code, clicks_count=click_count)

# Эндпоинт для главной страницы
@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

# Создание всех таблиц в БД
Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    app.run(debug=True)
