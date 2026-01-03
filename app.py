from flask import Flask, request, jsonify, render_template
from sqlalchemy import create_engine, Column, Text, DateTime, ForeignKey
from sqlalchemy.dialects.sqlite import VARCHAR
from sqlalchemy.orm import sessionmaker, relationship, declarative_base
from sqlalchemy.sql import func
import uuid
import random
import string
from config import DATABASE_URL

# Создание объекта Flask
app = Flask(__name__)

# Создание подключения к базе данных SQLite
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Создание сессии
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Создание Base
Base = declarative_base()


class ShortLink(Base):
    __tablename__ = "short_links"

    id = Column(VARCHAR(36), primary_key=True, default=str(uuid.uuid4))
    original_url = Column(Text, nullable=False)
    short_code = Column(VARCHAR(10), unique=True, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    expires_at = Column(DateTime, nullable=True)


class Click(Base):
    __tablename__ = "clicks"

    id = Column(VARCHAR(36), primary_key=True, default=str(uuid.uuid4))
    link_id = Column(VARCHAR(36), ForeignKey('short_links.id'), nullable=False)
    clicked_at = Column(DateTime, server_default=func.now())
    ip_address = Column(Text, nullable=True)
    user_agent = Column(Text, nullable=True)
    referer = Column(Text, nullable=True)

    # Связь с сокращённой ссылкой
    link = relationship("ShortLink", backref="clicks")


def generate_short_code(length=10):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


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


@app.route("/stats/<short_code>", methods=["GET"])
def get_stats(short_code):
    db = next(get_db())
    db_link = db.query(ShortLink).filter(ShortLink.short_code == short_code).first()
    if db_link is None:
        return jsonify({"error": "Link not found"}), 404

    # Получаем количество кликов
    click_count = db.query(Click).filter(Click.link_id == db_link.id).count()

    return render_template("stats.html", short_code=short_code, clicks_count=click_count)


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    app.run(debug=True)
