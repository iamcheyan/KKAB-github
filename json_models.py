"""JSON-based data models for the GuestHouse application."""
import json
import os
from datetime import datetime, date
from typing import Dict, List, Optional, Any, Union
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import UserMixin


class JSONDataManager:
    """Base class for managing JSON data files."""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
    
    def _get_file_path(self, filename: str) -> str:
        """Get the full path for a data file."""
        return os.path.join(self.data_dir, filename)
    
    def _load_json(self, filename: str) -> List[Dict]:
        """Load data from a JSON file."""
        file_path = self._get_file_path(filename)
        if not os.path.exists(file_path):
            return []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []
    
    def _save_json(self, filename: str, data: List[Dict]) -> None:
        """Save data to a JSON file."""
        file_path = self._get_file_path(filename)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=self._json_serializer)
    
    def _json_serializer(self, obj):
        """Custom JSON serializer for datetime objects."""
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
    
    def _get_next_id(self, data: List[Dict]) -> int:
        """Get the next available ID."""
        if not data:
            return 1
        return max(item.get('id', 0) for item in data) + 1


class Room:
    """Represents a room type that can be booked."""
    
    def __init__(self, data_manager: JSONDataManager):
        self.data_manager = data_manager
        self.filename = "rooms.json"
    
    def create(self, **kwargs) -> Dict:
        """Create a new room."""
        rooms = self.data_manager._load_json(self.filename)
        room_data = {
            'id': self.data_manager._get_next_id(rooms),
            'name': kwargs.get('name', ''),
            'description': kwargs.get('description', ''),
            'price': kwargs.get('price', 0.0),
            'capacity': kwargs.get('capacity', 1),
            'image': kwargs.get('image', 'img/placeholder.jpg'),
            'status': kwargs.get('status', '空室あり'),
            'name_ja': kwargs.get('name_ja'),
            'name_en': kwargs.get('name_en'),
            'name_zh': kwargs.get('name_zh'),
            'description_ja': kwargs.get('description_ja'),
            'description_en': kwargs.get('description_en'),
            'description_zh': kwargs.get('description_zh'),
            'airbnb_url': kwargs.get('airbnb_url'),
            'address_ja': kwargs.get('address_ja'),
            'address_en': kwargs.get('address_en'),
            'address_zh': kwargs.get('address_zh'),
            'permit_number': kwargs.get('permit_number'),
        }
        rooms.append(room_data)
        self.data_manager._save_json(self.filename, rooms)
        return room_data
    
    def get_all(self) -> List[Dict]:
        """Get all rooms."""
        return self.data_manager._load_json(self.filename)
    
    def get_by_id(self, room_id: int) -> Optional[Dict]:
        """Get a room by ID."""
        rooms = self.data_manager._load_json(self.filename)
        for room in rooms:
            if room.get('id') == room_id:
                return room
        return None
    
    def update(self, room_id: int, **kwargs) -> bool:
        """Update a room."""
        rooms = self.data_manager._load_json(self.filename)
        for i, room in enumerate(rooms):
            if room.get('id') == room_id:
                for key, value in kwargs.items():
                    if key != 'id':  # Don't allow ID changes
                        room[key] = value
                self.data_manager._save_json(self.filename, rooms)
                return True
        return False
    
    def delete(self, room_id: int) -> bool:
        """Delete a room."""
        rooms = self.data_manager._load_json(self.filename)
        rooms = [room for room in rooms if room.get('id') != room_id]
        self.data_manager._save_json(self.filename, rooms)
        return True


class Booking:
    """Stores a reservation made by a guest."""
    
    def __init__(self, data_manager: JSONDataManager):
        self.data_manager = data_manager
        self.filename = "bookings.json"
    
    def create(self, **kwargs) -> Dict:
        """Create a new booking."""
        bookings = self.data_manager._load_json(self.filename)
        booking_data = {
            'id': self.data_manager._get_next_id(bookings),
            'room_id': kwargs.get('room_id'),
            'name': kwargs.get('name', ''),
            'email': kwargs.get('email', ''),
            'check_in': kwargs.get('check_in'),
            'check_out': kwargs.get('check_out'),
            'guests': kwargs.get('guests', 1),
            'status': kwargs.get('status', 'Pending'),
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': kwargs.get('updated_at'),
        }
        bookings.append(booking_data)
        self.data_manager._save_json(self.filename, bookings)
        return booking_data
    
    def get_all(self) -> List[Dict]:
        """Get all bookings."""
        return self.data_manager._load_json(self.filename)
    
    def get_by_id(self, booking_id: int) -> Optional[Dict]:
        """Get a booking by ID."""
        bookings = self.data_manager._load_json(self.filename)
        for booking in bookings:
            if booking.get('id') == booking_id:
                return booking
        return None
    
    def get_by_room_id(self, room_id: int) -> List[Dict]:
        """Get all bookings for a specific room."""
        bookings = self.data_manager._load_json(self.filename)
        return [booking for booking in bookings if booking.get('room_id') == room_id]
    
    def update(self, booking_id: int, **kwargs) -> bool:
        """Update a booking."""
        bookings = self.data_manager._load_json(self.filename)
        for i, booking in enumerate(bookings):
            if booking.get('id') == booking_id:
                for key, value in kwargs.items():
                    if key != 'id':  # Don't allow ID changes
                        booking[key] = value
                booking['updated_at'] = datetime.utcnow().isoformat()
                self.data_manager._save_json(self.filename, bookings)
                return True
        return False
    
    def delete(self, booking_id: int) -> bool:
        """Delete a booking."""
        bookings = self.data_manager._load_json(self.filename)
        bookings = [booking for booking in bookings if booking.get('id') != booking_id]
        self.data_manager._save_json(self.filename, bookings)
        return True


class Message:
    """Contact form submissions."""
    
    def __init__(self, data_manager: JSONDataManager):
        self.data_manager = data_manager
        self.filename = "messages.json"
    
    def create(self, **kwargs) -> Dict:
        """Create a new message."""
        messages = self.data_manager._load_json(self.filename)
        message_data = {
            'id': self.data_manager._get_next_id(messages),
            'name': kwargs.get('name', ''),
            'email': kwargs.get('email', ''),
            'content': kwargs.get('content', ''),
            'created_at': datetime.utcnow().isoformat(),
            'name_ja': kwargs.get('name_ja'),
            'name_en': kwargs.get('name_en'),
            'name_zh': kwargs.get('name_zh'),
            'content_ja': kwargs.get('content_ja'),
            'content_en': kwargs.get('content_en'),
            'content_zh': kwargs.get('content_zh'),
            'reply_ja': kwargs.get('reply_ja'),
            'reply_en': kwargs.get('reply_en'),
            'reply_zh': kwargs.get('reply_zh'),
            'is_replied': kwargs.get('is_replied', False),
            'replied_at': kwargs.get('replied_at'),
        }
        messages.append(message_data)
        self.data_manager._save_json(self.filename, messages)
        return message_data
    
    def get_all(self) -> List[Dict]:
        """Get all messages."""
        return self.data_manager._load_json(self.filename)
    
    def get_by_id(self, message_id: int) -> Optional[Dict]:
        """Get a message by ID."""
        messages = self.data_manager._load_json(self.filename)
        for message in messages:
            if message.get('id') == message_id:
                return message
        return None
    
    def update(self, message_id: int, **kwargs) -> bool:
        """Update a message."""
        messages = self.data_manager._load_json(self.filename)
        for i, message in enumerate(messages):
            if message.get('id') == message_id:
                for key, value in kwargs.items():
                    if key != 'id':  # Don't allow ID changes
                        message[key] = value
                self.data_manager._save_json(self.filename, messages)
                return True
        return False
    
    def delete(self, message_id: int) -> bool:
        """Delete a message."""
        messages = self.data_manager._load_json(self.filename)
        messages = [message for message in messages if message.get('id') != message_id]
        self.data_manager._save_json(self.filename, messages)
        return True


class Admin(UserMixin):
    """Administrative user able to manage the site."""
    
    def __init__(self, data_manager: JSONDataManager):
        self.data_manager = data_manager
        self.filename = "admins.json"
        self.id = None
        self.username = None
        self.password_hash = None
    
    @classmethod
    def create(cls, data_manager: JSONDataManager, **kwargs) -> Dict:
        """Create a new admin user."""
        admins = data_manager._load_json("admins.json")
        admin_data = {
            'id': data_manager._get_next_id(admins),
            'username': kwargs.get('username', ''),
            'password_hash': kwargs.get('password_hash', ''),
        }
        admins.append(admin_data)
        data_manager._save_json("admins.json", admins)
        return admin_data
    
    @classmethod
    def get_by_username(cls, data_manager: JSONDataManager, username: str) -> Optional['Admin']:
        """Get an admin by username."""
        admins = data_manager._load_json("admins.json")
        for admin_data in admins:
            if admin_data.get('username') == username:
                admin = cls(data_manager)
                admin.id = admin_data.get('id')
                admin.username = admin_data.get('username')
                admin.password_hash = admin_data.get('password_hash')
                return admin
        return None
    
    @classmethod
    def get_all(cls, data_manager: JSONDataManager) -> List[Dict]:
        """Get all admin users."""
        return data_manager._load_json("admins.json")
    
    @classmethod
    def get_by_id(cls, data_manager: JSONDataManager, admin_id: int) -> Optional['Admin']:
        """Get an admin by ID."""
        admins = data_manager._load_json("admins.json")
        for admin_data in admins:
            if admin_data.get('id') == admin_id:
                admin = cls(data_manager)
                admin.id = admin_data.get('id')
                admin.username = admin_data.get('username')
                admin.password_hash = admin_data.get('password_hash')
                return admin
        return None
    
    def set_password(self, password: str) -> None:
        """Hash and store the provided password."""
        self.password_hash = generate_password_hash(password, method="pbkdf2:sha256")
    
    def check_password(self, password: str) -> bool:
        """Validate the provided password against the stored hash."""
        return check_password_hash(self.password_hash, password)
    
    def save(self) -> bool:
        """Save the admin user."""
        admins = self.data_manager._load_json(self.filename)
        for i, admin in enumerate(admins):
            if admin.get('id') == self.id:
                admin['username'] = self.username
                admin['password_hash'] = self.password_hash
                self.data_manager._save_json(self.filename, admins)
                return True
        return False


class News:
    """Informational articles shown on the public site."""
    
    def __init__(self, data_manager: JSONDataManager):
        self.data_manager = data_manager
        self.filename = "news.json"
    
    def create(self, **kwargs) -> Dict:
        """Create a new news article."""
        news_list = self.data_manager._load_json(self.filename)
        news_data = {
            'id': self.data_manager._get_next_id(news_list),
            'title_ja': kwargs.get('title_ja', ''),
            'title_en': kwargs.get('title_en', ''),
            'title_zh': kwargs.get('title_zh', ''),
            'body_ja': kwargs.get('body_ja', ''),
            'body_en': kwargs.get('body_en', ''),
            'body_zh': kwargs.get('body_zh', ''),
            'published_at': kwargs.get('published_at', datetime.utcnow().isoformat()),
            'is_published': kwargs.get('is_published', True),
        }
        news_list.append(news_data)
        self.data_manager._save_json(self.filename, news_list)
        return news_data
    
    def get_all(self) -> List[Dict]:
        """Get all news articles."""
        return self.data_manager._load_json(self.filename)
    
    def get_published(self) -> List[Dict]:
        """Get all published news articles."""
        news_list = self.data_manager._load_json(self.filename)
        return [news for news in news_list if news.get('is_published', True)]
    
    def get_by_id(self, news_id: int) -> Optional[Dict]:
        """Get a news article by ID."""
        news_list = self.data_manager._load_json(self.filename)
        for news in news_list:
            if news.get('id') == news_id:
                return news
        return None
    
    def update(self, news_id: int, **kwargs) -> bool:
        """Update a news article."""
        news_list = self.data_manager._load_json(self.filename)
        for i, news in enumerate(news_list):
            if news.get('id') == news_id:
                for key, value in kwargs.items():
                    if key != 'id':  # Don't allow ID changes
                        news[key] = value
                self.data_manager._save_json(self.filename, news_list)
                return True
        return False
    
    def delete(self, news_id: int) -> bool:
        """Delete a news article."""
        news_list = self.data_manager._load_json(self.filename)
        news_list = [news for news in news_list if news.get('id') != news_id]
        self.data_manager._save_json(self.filename, news_list)
        return True


class SiteContent:
    """Stores editable contact or informational blocks per language."""
    
    def __init__(self, data_manager: JSONDataManager):
        self.data_manager = data_manager
        self.filename = "site_content.json"
    
    def create(self, **kwargs) -> Dict:
        """Create a new site content block."""
        content_list = self.data_manager._load_json(self.filename)
        content_data = {
            'id': self.data_manager._get_next_id(content_list),
            'key': kwargs.get('key', ''),
            'heading_ja': kwargs.get('heading_ja', ''),
            'heading_en': kwargs.get('heading_en', ''),
            'heading_zh': kwargs.get('heading_zh', ''),
            'body_ja': kwargs.get('body_ja', ''),
            'body_en': kwargs.get('body_en', ''),
            'body_zh': kwargs.get('body_zh', ''),
            'extra': kwargs.get('extra'),
        }
        content_list.append(content_data)
        self.data_manager._save_json(self.filename, content_list)
        return content_data
    
    def get_all(self) -> List[Dict]:
        """Get all site content blocks."""
        return self.data_manager._load_json(self.filename)
    
    def get_by_key(self, key: str) -> Optional[Dict]:
        """Get a site content block by key."""
        content_list = self.data_manager._load_json(self.filename)
        for content in content_list:
            if content.get('key') == key:
                return content
        return None
    
    def get_by_id(self, content_id: int) -> Optional[Dict]:
        """Get a site content block by ID."""
        content_list = self.data_manager._load_json(self.filename)
        for content in content_list:
            if content.get('id') == content_id:
                return content
        return None
    
    def update(self, content_id: int, **kwargs) -> bool:
        """Update a site content block."""
        content_list = self.data_manager._load_json(self.filename)
        for i, content in enumerate(content_list):
            if content.get('id') == content_id:
                for key, value in kwargs.items():
                    if key != 'id':  # Don't allow ID changes
                        content[key] = value
                self.data_manager._save_json(self.filename, content_list)
                return True
        return False
    
    def update_by_key(self, key: str, **kwargs) -> bool:
        """Update a site content block by key."""
        content_list = self.data_manager._load_json(self.filename)
        for i, content in enumerate(content_list):
            if content.get('key') == key:
                for k, value in kwargs.items():
                    if k != 'id' and k != 'key':  # Don't allow ID or key changes
                        content[k] = value
                self.data_manager._save_json(self.filename, content_list)
                return True
        return False
    
    def delete(self, content_id: int) -> bool:
        """Delete a site content block."""
        content_list = self.data_manager._load_json(self.filename)
        content_list = [content for content in content_list if content.get('id') != content_id]
        self.data_manager._save_json(self.filename, content_list)
        return True


# Global instances
data_manager = JSONDataManager()
room_model = Room(data_manager)
booking_model = Booking(data_manager)
message_model = Message(data_manager)
news_model = News(data_manager)
site_content_model = SiteContent(data_manager)