"""Database models for the GuestHouse application."""
from datetime import datetime

from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash

# Global SQLAlchemy instance that will be initialized by the Flask app.
db = SQLAlchemy()


class Room(db.Model):
    """Represents a room type that can be booked."""

    id = db.Column(db.Integer, primary_key=True)
    # Legacy default fields retained for backward compatibility; Japanese content is stored here.
    name = db.Column(db.String(80), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    image = db.Column(db.String(120), nullable=False, default="img/placeholder.jpg")
    status = db.Column(db.String(20), nullable=False, default="空室あり")
    name_ja = db.Column(db.String(120))
    name_en = db.Column(db.String(120))
    name_zh = db.Column(db.String(120))
    description_ja = db.Column(db.Text)
    description_en = db.Column(db.Text)
    description_zh = db.Column(db.Text)
    airbnb_url = db.Column(db.String(255))
    address_ja = db.Column(db.String(255))
    address_en = db.Column(db.String(255))
    address_zh = db.Column(db.String(255))
    permit_number = db.Column(db.String(120))

    bookings = db.relationship("Booking", back_populates="room", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Room {self.name}>"


class Booking(db.Model):
    """Stores a reservation made by a guest."""

    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey("room.id"), nullable=False)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    check_in = db.Column(db.Date, nullable=False)
    check_out = db.Column(db.Date, nullable=False)
    guests = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), nullable=False, default="Pending")
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    room = db.relationship("Room", back_populates="bookings")

    def __repr__(self):
        return f"<Booking {self.name} - {self.room.name}>"


class Message(db.Model):
    """Contact form submissions."""

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<Message from {self.name}>"


class Admin(UserMixin, db.Model):
    """Administrative user able to manage the site."""

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def set_password(self, password: str) -> None:
        """Hash and store the provided password."""
        # Explicitly use pbkdf2 for compatibility with older Python builds lacking scrypt.
        self.password_hash = generate_password_hash(password, method="pbkdf2:sha256")

    def check_password(self, password: str) -> bool:
        """Validate the provided password against the stored hash."""
        return check_password_hash(self.password_hash, password)


class News(db.Model):
    """Informational articles shown on the public site."""

    id = db.Column(db.Integer, primary_key=True)
    title_ja = db.Column(db.String(160), nullable=False)
    title_en = db.Column(db.String(160), nullable=False)
    title_zh = db.Column(db.String(160), nullable=False)
    body_ja = db.Column(db.Text, nullable=False)
    body_en = db.Column(db.Text, nullable=False)
    body_zh = db.Column(db.Text, nullable=False)
    published_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    is_published = db.Column(db.Boolean, default=True, nullable=False)


class SiteContent(db.Model):
    """Stores editable contact or informational blocks per language."""

    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(80), unique=True, nullable=False)
    heading_ja = db.Column(db.String(160), nullable=False)
    heading_en = db.Column(db.String(160), nullable=False)
    heading_zh = db.Column(db.String(160), nullable=False)
    body_ja = db.Column(db.Text, nullable=False)
    body_en = db.Column(db.Text, nullable=False)
    body_zh = db.Column(db.Text, nullable=False)
    extra = db.Column(db.JSON, nullable=True)


__all__ = [
    "db",
    "Room",
    "Booking",
    "Message",
    "Admin",
    "News",
    "SiteContent",
]
