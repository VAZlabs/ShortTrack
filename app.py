from flask import (
    Flask,
    request,
    jsonify,
    render_template,
    redirect,
    url_for
)
from sqlalchemy import create_engine, Column, Text, DateTime, ForeignKey
from sqlalchemy.dialects.sqlite import VARCHAR
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from sqlalchemy.sql import func
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
import random
import string
from config import DATABASE_URL


# Create Flask app instance
app = Flask(__name__)

# Create connection to SQLite database
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)  # SQLite requires connect_args

# Create session to interact with the database
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base for the models
Base = declarative_base()


# User model for storing user data
class User(Base):
    __tablename__ = "users"

    id = Column(VARCHAR(36), primary_key=True, default=str(uuid.uuid4))
    username = Column(VARCHAR(50), unique=True, nullable=False)
    email = Column(VARCHAR(100), unique=True, nullable=False)
    password_hash = Column(Text, nullable=False)
    created_at = Column(DateTime, server_default=func.now())


# ShortLink model for URL shortening
class ShortLink(Base):
    __tablename__ = "short_links"

    id = Column(VARCHAR(36), primary_key=True, default=str(uuid.uuid4))
    short_code = Column(VARCHAR(10), unique=True, nullable=False)
    original_url = Column(Text, nullable=False)


# Click model for tracking link clicks
class Click(Base):
    __tablename__ = "clicks"

    id = Column(VARCHAR(36), primary_key=True, default=str(uuid.uuid4))
    link_id = Column(VARCHAR(36), ForeignKey("short_links.id"), nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    # Defining the relationship
    link = relationship("ShortLink", backref="clicks")


# Create tables in the database if they do not exist
Base.metadata.create_all(bind=engine)


# Function to generate random short codes
def generate_short_code(length=10):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))


# Get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Route for home page
@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


# Route for user registration
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        # Hash the password before saving to the database
        password_hash = generate_password_hash(password)

        # Add new user to the database
        db = next(get_db())
        db_user = User(
            username=username,
            email=email,
            password_hash=password_hash
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)

        return redirect(url_for("login"))  # Redirect to login after success

    return render_template("register.html")


# Route for user login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        # Fetch user by email from the database
        db = next(get_db())
        user = db.query(User).filter(User.email == email).first()

        if user and check_password_hash(user.password_hash, password):
            return redirect(url_for("index"))  # Success

        return "Invalid credentials. Please try again."

    return render_template("login.html")


# Route for user stats
@app.route("/stats/<short_code>", methods=["GET"])
def get_stats(short_code):
    db = next(get_db())
    db_link = db.query(ShortLink).filter(
        ShortLink.short_code == short_code
    ).first()
    if db_link is None:
        return jsonify({"error": "Link not found"}), 404

    # Get click count
    click_count = db.query(Click).filter(
        Click.link_id == db_link.id
    ).count()

    return render_template(
        "stats.html",
        short_code=short_code,
        clicks_count=click_count
    )


# Route for creating a short URL (for testing)
@app.route("/shorten", methods=["POST"])
def shorten_url():
    original_url = request.json.get("original_url")
    short_code = generate_short_code()
    return jsonify({
        "short_code": short_code,
        "original_url": original_url
    })


if __name__ == "__main__":
    app.run(debug=True)
