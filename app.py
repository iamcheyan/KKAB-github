"""Flask application entry point for the GuestHouse site."""
from __future__ import annotations

import os
import uuid
import subprocess
import tempfile
import shutil
from datetime import date, datetime, timedelta
from werkzeug.utils import secure_filename

from flask import Flask, flash, redirect, render_template, request, session, url_for, jsonify, send_file
from flask_login import LoginManager, current_user, login_required, login_user, logout_user
from flask_wtf import CSRFProtect, FlaskForm
from flask_wtf.file import FileField
from werkzeug.datastructures import FileStorage
from wtforms.validators import DataRequired
from sqlalchemy import inspect, text
from urllib.parse import urljoin, urlparse

from forms import (
    BookingForm,
    ContactContentForm,
    ContactForm,
    LoginForm,
    NewsForm,
    HomeContentForm,
    RoomAdminForm,
    UserManagementForm,
    ChangePasswordForm,
)
from models import Admin, Booking, Message, News, Room, SiteContent, db
from translations import DEFAULT_LANGUAGE, LANGUAGES, TRANSLATIONS


csrf = CSRFProtect()


def create_app() -> Flask:
    """Application factory configuring Flask, database, and login."""
    app = Flask(__name__, template_folder='templates', static_folder='static')
    app.config.update(
        SECRET_KEY=os.environ.get("SECRET_KEY", "dev-secret-key"),
        SQLALCHEMY_DATABASE_URI=f"sqlite:///{os.path.abspath('db.db')}",
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )
    
    # JSONデータ読み込み関数
    def load_home_content():
        import json
        json_file_path = os.path.join(app.static_folder, 'data', 'home_content.json')
        if os.path.exists(json_file_path):
            with open(json_file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    # ユーザー管理JSONファイル操作関数
    def load_users():
        import json
        users_file_path = 'users.json'
        if os.path.exists(users_file_path):
            with open(users_file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []

    def save_users(users):
        import json
        users_file_path = 'users.json'
        with open(users_file_path, 'w', encoding='utf-8') as f:
            json.dump(users, f, ensure_ascii=False, indent=2)

    def add_user_to_json(username, password):
        users = load_users()
        # ユーザーが既に存在するかチェック
        for user in users:
            if user['username'] == username:
                return False
        users.append({'username': username, 'password': password})
        save_users(users)
        return True

    def update_user_password(username, new_password):
        users = load_users()
        for user in users:
            if user['username'] == username:
                user['password'] = new_password
                save_users(users)
                return True
        return False

    def delete_user_from_json(username):
        users = load_users()
        users = [user for user in users if user['username'] != username]
        save_users(users)
        return True
    
    # 関数をアプリケーションコンテキストに追加
    app.load_home_content = load_home_content
    app.load_users = load_users
    app.add_user_to_json = add_user_to_json
    app.update_user_password = update_user_password
    app.delete_user_from_json = delete_user_from_json

    db.init_app(app)
    csrf.init_app(app)

    def get_locale() -> str:
        locale = session.get("locale", DEFAULT_LANGUAGE)
        if locale not in LANGUAGES:
            locale = DEFAULT_LANGUAGE
        return locale

    def translate(key: str, **kwargs) -> str:
        entry = TRANSLATIONS.get(key, {})
        text = entry.get(get_locale()) or entry.get(DEFAULT_LANGUAGE) or key
        if kwargs:
            try:
                text = text.format(**kwargs)
            except Exception:
                pass
        return text

    def localized_attr(model, base: str) -> str:
        locale = get_locale()
        attr_name = f"{base}_{locale}"
        if hasattr(model, attr_name):
            value = getattr(model, attr_name)
            if value:
                return value
        fallback = getattr(model, base, None)
        if fallback:
            return fallback
        default_attr = f"{base}_{DEFAULT_LANGUAGE}"
        return getattr(model, default_attr, "")

    def is_safe_redirect(target: str) -> bool:
        ref_url = urlparse(request.host_url)
        test_url = urlparse(urljoin(request.host_url, target))
        return test_url.scheme in {"http", "https"} and ref_url.netloc == test_url.netloc

    # 确保数据库文件存在，如果不存在则创建基本表结构
    with app.app_context():
        db_path = "db.db"
        
        # 打印当前使用的数据库地址
        print(f"当前使用的数据库地址: {app.config['SQLALCHEMY_DATABASE_URI']}")
        print(f"数据库文件路径: {os.path.abspath(db_path)}")
        
        # 如果数据库文件不存在，提示用户并退出
        if not os.path.exists(db_path):
            print("错误：数据库文件 db.db 不存在！")
            print("请恢复数据库文件后再启动应用程序。")
            print("可以使用备份文件：backups/latest.sql 或 backups/guesthouse_backup_*.sql")
            import sys
            sys.exit(1)
        else:
            print("使用现有的数据库文件")
            # 只确保表结构存在，不插入数据
            db.create_all()

        # 确保多语言字段存在（向后兼容）
        inspector = inspect(db.engine)

        def ensure_column(table: str, column: str, ddl: str) -> None:
            """Add a column to an existing table if it's missing."""
            nonlocal inspector
            try:
                if column not in {col["name"] for col in inspector.get_columns(table)}:
                    db.session.execute(text(f"ALTER TABLE {table} ADD COLUMN {column} {ddl}"))
                    db.session.commit()
                    # Refresh inspector metadata for subsequent checks.
                    inspector = inspect(db.engine)
            except Exception as e:
                print(f"警告：无法添加列 {table}.{column}: {e}")

        # 确保多语言字段和Airbnb链接存在于旧数据库中
        ensure_column("room", "name_ja", "VARCHAR(120)")
        ensure_column("room", "name_en", "VARCHAR(120)")
        ensure_column("room", "name_zh", "VARCHAR(120)")
        ensure_column("room", "description_ja", "TEXT")
        ensure_column("room", "description_en", "TEXT")
        ensure_column("room", "description_zh", "TEXT")
        ensure_column("room", "airbnb_url", "VARCHAR(255)")
        ensure_column("room", "address_ja", "VARCHAR(255)")
        ensure_column("room", "address_en", "VARCHAR(255)")
        ensure_column("room", "address_zh", "VARCHAR(255)")
        ensure_column("room", "permit_number", "VARCHAR(120)")

        # 确保多语言字段存在于news表
        ensure_column("news", "title_ja", "VARCHAR(200)")
        ensure_column("news", "title_en", "VARCHAR(200)")
        ensure_column("news", "title_zh", "VARCHAR(200)")
        ensure_column("news", "body_ja", "TEXT")
        ensure_column("news", "body_en", "TEXT")
        ensure_column("news", "body_zh", "TEXT")
        ensure_column("news", "is_published", "BOOLEAN")

        # 确保多语言字段存在于site_content表
        ensure_column("site_content", "heading_ja", "VARCHAR(200)")
        ensure_column("site_content", "heading_en", "VARCHAR(200)")
        ensure_column("site_content", "heading_zh", "VARCHAR(200)")
        ensure_column("site_content", "body_ja", "TEXT")
        ensure_column("site_content", "body_en", "TEXT")
        ensure_column("site_content", "body_zh", "TEXT")
        ensure_column("site_content", "extra", "TEXT")

        # 确保多语言字段存在于message表
        ensure_column("message", "name_ja", "VARCHAR(100)")
        ensure_column("message", "name_en", "VARCHAR(100)")
        ensure_column("message", "name_zh", "VARCHAR(100)")
        ensure_column("message", "content_ja", "TEXT")
        ensure_column("message", "content_en", "TEXT")
        ensure_column("message", "content_zh", "TEXT")
        ensure_column("message", "reply_ja", "TEXT")
        ensure_column("message", "reply_en", "TEXT")
        ensure_column("message", "reply_zh", "TEXT")
        ensure_column("message", "is_replied", "BOOLEAN")
        ensure_column("message", "replied_at", "DATETIME")

        # 确保admin表有password_hash列
        ensure_column("admin", "password_hash", "VARCHAR(128)")

        # 确保booking表有所有必需的列
        ensure_column("booking", "status", "VARCHAR(20)")
        ensure_column("booking", "created_at", "DATETIME")
        ensure_column("booking", "updated_at", "DATETIME")

        # 检查数据库状态
        room_count = Room.query.count()
        admin_count = Admin.query.count()
        print(f"数据库状态：{room_count} 个房间，{admin_count} 个管理员账户")
        
        if admin_count == 0:
            print("警告：数据库中没有管理员账户，请通过管理界面创建管理员账户")

        # 数据规范化处理（仅处理现有数据）
        rooms_in_db = Room.query.all()
        normalized = False
        for room in rooms_in_db:
            if room.image:
                cleaned = room.image.lstrip("/")
                if cleaned.startswith("static/"):
                    cleaned = cleaned[len("static/") :]
                if cleaned != room.image:
                    room.image = cleaned
                    normalized = True

            if room.status == "Available":
                room.status = "空室あり"
                normalized = True

            # 确保多语言字段有默认值
            if not room.name_ja:
                room.name_ja = room.name
                normalized = True
            if not room.description_ja:
                room.description_ja = room.description
                normalized = True
            if not room.name_en:
                room.name_en = room.name
                normalized = True
            if not room.description_en:
                room.description_en = room.description
                normalized = True
            if not room.name_zh:
                room.name_zh = room.name
                normalized = True
            if not room.description_zh:
                room.description_zh = room.description
                normalized = True

        if normalized:
            db.session.commit()
            print("已更新房间数据的格式")

    login_manager = LoginManager(app)
    login_manager.login_view = "admin_login"

    @login_manager.user_loader
    def load_user(user_id: str):
        return Admin.query.get(int(user_id))

    @app.context_processor
    def inject_globals():
        def media_url(path: str | None, default: str = "img/placeholder.jpg") -> str:
            candidate = (path or default).strip()
            if candidate.startswith(("http://", "https://")):
                candidate = default

            cleaned = candidate.lstrip("/")
            if cleaned.startswith("static/"):
                cleaned = cleaned[len("static/") :]

            if not cleaned:
                cleaned = default

            asset_path = os.path.join(app.static_folder, cleaned)
            if not os.path.exists(asset_path):
                fallback = default.lstrip("/")
                if fallback.startswith("static/"):
                    fallback = fallback[len("static/") :]
                cleaned = fallback

            return url_for("static", filename=cleaned)

        room_status_labels = {
            "Available": "room.status.available",
            "空室あり": "room.status.available",
            "満室": "room.status.booked",
            "Booked": "room.status.booked",
            "準備中": "room.status.prep",
            "Preparing": "room.status.prep",
        }
        booking_status_labels = {
            "Pending": "booking.status.pending",
            "確認待ち": "booking.status.pending",
            "Confirmed": "booking.status.confirmed",
            "確定": "booking.status.confirmed",
            "Cancelled": "booking.status.cancelled",
            "キャンセル": "booking.status.cancelled",
        }

        def room_status_label(status: str) -> str:
            key = room_status_labels.get(status, "room.status.available")
            return translate(key)

        def booking_status_label(status: str) -> str:
            key = booking_status_labels.get(status, "booking.status.pending")
            return translate(key)

        # Lazy load homepage content once per request
        _home_cache = {"loaded": False, "content": None}

        def home_text(key: str) -> str:
            if not _home_cache["loaded"]:
                _home_cache["content"] = SiteContent.query.filter_by(key="home").first()
                _home_cache["loaded"] = True
            content: SiteContent | None = _home_cache["content"]
            locale = get_locale()

            # Fallback map to translation keys
            fallback_map = {
                "kicker": "hero.kicker",
                "heading": "hero.title",
                "body": "hero.subtitle",
                "badge": "hero.badge",
                "point1": "hero.point1",
                "point2": "hero.point2",
                "point3": "hero.point3",
                "info_hours": "hero.info.hours",
                "info_station": "hero.info.station",
                "cta_book": "hero.cta_book",
                "cta_rooms": "hero.cta_rooms",
            }

            if not content:
                return translate(fallback_map.get(key, ""))

            if key == "heading":
                return getattr(content, f"heading_{locale}") or translate("hero.title")
            if key == "body":
                return getattr(content, f"body_{locale}") or translate("hero.subtitle")

            extra = content.extra or {}
            node = extra.get(key, {})
            value = node.get(locale)
            if value:
                return value
            return translate(fallback_map.get(key, ""))

        return {
            "today": date.today(),
            "media_url": media_url,
            "room_status": room_status_label,
            "booking_status": booking_status_label,
            "t": translate,
            "languages": LANGUAGES,
            "current_locale": get_locale(),
            "localize": localized_attr,
            "home": home_text,
        }

    def _allowed_file(filename):
        """Check if the uploaded file has an allowed extension."""
        ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'avif'}
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    def _save_uploaded_file(file, room_id=None):
        """Save uploaded file and return the relative path."""
        if file and _allowed_file(file.filename):
            # Create upload directory if it doesn't exist
            upload_dir = os.path.join(app.static_folder, 'img', 'rooms')
            os.makedirs(upload_dir, exist_ok=True)
            
            # Generate unique filename
            filename = secure_filename(file.filename)
            name, ext = os.path.splitext(filename)
            if room_id:
                unique_filename = f"room_{room_id}_{uuid.uuid4().hex[:8]}{ext}"
            else:
                unique_filename = f"room_new_{uuid.uuid4().hex[:8]}{ext}"
            
            # Save file
            file_path = os.path.join(upload_dir, unique_filename)
            file.save(file_path)
            
            # Return relative path for database storage
            return f"img/rooms/{unique_filename}"
        return None

    def _update_room_from_form(room: Room, form: RoomAdminForm) -> None:
        room.name_ja = form.name_ja.data
        room.name_en = form.name_en.data
        room.name_zh = form.name_zh.data
        room.description_ja = form.description_ja.data
        room.description_en = form.description_en.data
        room.description_zh = form.description_zh.data
        room.address_ja = form.address_ja.data
        room.address_en = form.address_en.data
        room.address_zh = form.address_zh.data
        room.permit_number = form.permit_number.data
        
        # Handle image upload
        if form.image_file.data:
            # If new image is uploaded, save it and update the path
            new_image_path = _save_uploaded_file(form.image_file.data, room.id)
            if new_image_path:
                room.image = new_image_path
        else:
            # Keep existing image path
            room.image = form.image.data
            
        room.airbnb_url = form.airbnb_url.data
        # Legacy fields for simpler querying/default locale.
        room.name = room.name_ja
        room.description = room.description_ja

    def _update_news_from_form(news: News, form: NewsForm) -> None:
        news.title_ja = form.title_ja.data
        news.title_en = form.title_en.data
        news.title_zh = form.title_zh.data
        news.body_ja = form.body_ja.data
        news.body_en = form.body_en.data
        news.body_zh = form.body_zh.data
        news.is_published = form.is_published.data

    def _normalize_contact_extra(content: SiteContent | None) -> None:
        if not content:
            return

        def _clean_path(path: str | None) -> str:
            if not path:
                return ""
            cleaned = path.strip().lstrip("/")
            if cleaned.startswith("static/"):
                cleaned = cleaned[len("static/") :]
            return cleaned

        extra = dict(content.extra or {})
        updated = False

        wechat_path = _clean_path(extra.get("wechat_qr"))
        if not wechat_path or wechat_path.endswith("wechat_qr.svg"):
            wechat_path = "img/wx.jpg"
        if extra.get("wechat_qr") != wechat_path:
            extra["wechat_qr"] = wechat_path
            updated = True

        line_path = _clean_path(extra.get("line_qr")) or "img/line.jpg"
        if extra.get("line_qr") != line_path:
            extra["line_qr"] = line_path
            updated = True

        if updated:
            content.extra = extra
            db.session.commit()

    @app.route("/")
    def index():
        # Show a curated list of rooms and general description.
        featured_rooms = Room.query.limit(3).all()
        news_items = (
            News.query.filter_by(is_published=True)
            .order_by(News.published_at.desc())
            .limit(4)
            .all()
        )
        home_content = app.load_home_content()
        return render_template("index.html", rooms=featured_rooms, news_items=news_items, home_content=home_content)

    @app.route("/<locale>/")
    def index_with_locale(locale: str):
        if locale in LANGUAGES:
            session["locale"] = locale
        featured_rooms = Room.query.limit(3).all()
        news_items = (
            News.query.filter_by(is_published=True)
            .order_by(News.published_at.desc())
            .limit(4)
            .all()
        )
        home_content = app.load_home_content()
        return render_template("index.html", rooms=featured_rooms, news_items=news_items, home_content=home_content)

    @app.route("/management")
    def management():
        return render_template("management.html")

    @app.route("/<locale>/management")
    def management_with_locale(locale: str):
        if locale in LANGUAGES:
            session["locale"] = locale
        return render_template("management.html")

    @app.route("/lang/<locale>")
    def switch_language(locale: str):
        if locale not in LANGUAGES:
            locale = DEFAULT_LANGUAGE
        
        # 現在のページパスを取得
        current_path = request.args.get("next") or "/"
        
        # referrerが存在し、かつ当サイトのURLの場合、パス部分を抽出
        if request.referrer:
            try:
                from urllib.parse import urlparse
                parsed = urlparse(request.referrer)
                if parsed.netloc == request.host:  # 当サイトのURLであることを確認
                    current_path = parsed.path
            except:
                pass
        
        # 現在バックエンド管理ページにいる場合、管理ダッシュボードにリダイレクト
        if current_path.startswith('/admin'):
            return redirect(url_for('admin_dashboard'))
        
        # セッションに言語を設定
        session["locale"] = locale
        
        # 現在のパスを解析し、既存の言語プレフィックスを削除
        path_parts = current_path.strip("/").split("/")
        if path_parts and path_parts[0] in LANGUAGES:
            path_parts = path_parts[1:]  # 言語プレフィックスを削除
        
        # 新しいURLパスを構築
        if path_parts:
            new_path = f"/{locale}/{'/'.join(path_parts)}"
        else:
            new_path = f"/{locale}/"
            
        return redirect(new_path)

    @app.route("/rooms")
    def rooms():
        all_rooms = Room.query.all()
        return render_template("rooms.html", rooms=all_rooms)

    @app.route("/<locale>/rooms")
    def rooms_with_locale(locale: str):
        if locale in LANGUAGES:
            session["locale"] = locale
        all_rooms = Room.query.all()
        return render_template("rooms.html", rooms=all_rooms)

    @app.route("/rooms/<int:room_id>")
    def room_detail(room_id: int):
        room = Room.query.get_or_404(room_id)
        # 获取其他房间作为推荐房源（排除当前房间）
        recommended_rooms = Room.query.filter(Room.id != room_id).limit(3).all()
        return render_template("room_detail.html", room=room, recommended_rooms=recommended_rooms)

    @app.route("/<locale>/rooms/<int:room_id>")
    def room_detail_with_locale(locale: str, room_id: int):
        if locale in LANGUAGES:
            session["locale"] = locale
        room = Room.query.get_or_404(room_id)
        # 获取其他房间作为推荐房源（排除当前房间）
        recommended_rooms = Room.query.filter(Room.id != room_id).limit(3).all()
        return render_template("room_detail.html", room=room, recommended_rooms=recommended_rooms)

    @app.route("/booking")
    def booking():
        return redirect("https://www.airbnb.com/s?query=Kyoto", code=302)

    @app.route("/booking/success/<int:booking_id>")
    def booking_success(booking_id: int):
        booking_record = Booking.query.get_or_404(booking_id)
        return render_template("booking_success.html", booking=booking_record)

    @app.route("/contact", methods=["GET", "POST"])
    def contact():
        form = ContactForm()
        if form.validate_on_submit():
            message = Message(
                name=form.name.data,
                email=form.email.data,
                content=form.message.data,
            )
            db.session.add(message)
            db.session.commit()
            flash(translate("contact.flash.success"), "success")
            return redirect(url_for("contact"))
        
        # 获取联系信息内容
        contact_content = SiteContent.query.filter_by(key="contact").first()
        _normalize_contact_extra(contact_content)
        return render_template("contact.html", form=form, contact_content=contact_content)

    @app.route("/<locale>/contact", methods=["GET", "POST"])
    def contact_with_locale(locale: str):
        if locale in LANGUAGES:
            session["locale"] = locale
        form = ContactForm()
        if form.validate_on_submit():
            message = Message(
                name=form.name.data,
                email=form.email.data,
                content=form.message.data,
            )
            db.session.add(message)
            db.session.commit()
            flash(translate("contact.flash.success"), "success")
            return redirect(url_for("contact_with_locale", locale=locale))
        
        # 获取联系信息内容
        contact_content = SiteContent.query.filter_by(key="contact").first()
        _normalize_contact_extra(contact_content)
        return render_template("contact.html", form=form, contact_content=contact_content)

    @app.route("/admin/login", methods=["GET", "POST"])
    def admin_login():
        if current_user.is_authenticated:
            return redirect(url_for("admin_dashboard"))
        form = LoginForm()
        if form.validate_on_submit():
            admin = Admin.query.filter_by(username=form.username.data).first()
            if admin and admin.check_password(form.password.data):
                login_user(admin)
                flash("ログインしました", "success")
                return redirect(url_for("admin_dashboard"))
            flash("ユーザー名またはパスワードが正しくありません", "danger")
        return render_template("admin_login.html", form=form)

    @app.route("/admin/logout")
    @login_required
    def admin_logout():
        logout_user()
        flash("ログアウトしました", "info")
        return redirect(url_for("admin_login"))

    @app.route("/admin", methods=["GET", "POST"])
    @login_required
    def admin_dashboard():
        messages_count = Message.query.count()
        news_count = News.query.count()
        room_count = Room.query.count()
        last_backup_at = get_latest_backup_time()
        return render_template(
            "admin_dashboard.html",
            messages_count=messages_count,
            news_count=news_count,
            room_count=room_count,
            last_backup_at=last_backup_at,
            restore_form=RestoreBackupForm(),
        )

    @app.route("/admin/bookings")
    @login_required
    def admin_bookings():
        flash("予約は外部のAirbnbで受け付けます。", "info")
        return redirect(url_for("admin_dashboard"))

    @app.route("/admin/rooms")
    @login_required
    def admin_rooms():
        rooms = Room.query.order_by(Room.id).all()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            # AJAX请求，返回部分模板
            return render_template("admin_rooms_partial.html", rooms=rooms)
        else:
            # 直接访问，重定向到主页面
            return redirect(url_for("admin_dashboard"))

    @app.route("/admin/rooms/new", methods=["GET", "POST"])
    @login_required
    def admin_room_create():
        form = RoomAdminForm()
        if form.validate_on_submit():
            try:
                room = Room()
                _update_room_from_form(room, form)
                db.session.add(room)
                db.session.commit()
                flash("客室を作成しました", "success")
                return redirect(url_for("admin_rooms"))
            except Exception as e:
                db.session.rollback()
                flash(f"作成中にエラーが発生しました: {str(e)}", "error")
        return render_template("admin_room_form.html", form=form, is_edit=False)

    @app.route("/admin/rooms/<int:room_id>/edit", methods=["GET", "POST"])
    @login_required
    def admin_room_edit(room_id: int):
        room = Room.query.get_or_404(room_id)
        form = RoomAdminForm(obj=room)
        if form.validate_on_submit():
            try:
                _update_room_from_form(room, form)
                db.session.commit()
                flash("客室情報を更新しました", "success")
                return redirect(url_for("admin_rooms"))
            except Exception as e:
                db.session.rollback()
                flash(f"更新中にエラーが発生しました: {str(e)}", "error")
        return render_template("admin_room_form.html", form=form, is_edit=True, room=room)

    @app.route("/admin/rooms/<int:room_id>/delete", methods=["POST"])
    @login_required
    def admin_room_delete(room_id: int):
        room = Room.query.get_or_404(room_id)
        db.session.delete(room)
        db.session.commit()
        flash("客室を削除しました", "info")
        return redirect(url_for("admin_rooms"))

    @app.route("/admin/news")
    @login_required
    def admin_news():
        news_items = News.query.order_by(News.published_at.desc()).all()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return render_template("admin_news_partial.html", news_items=news_items)
        else:
            return redirect(url_for("admin_dashboard"))

    @app.route("/admin/news/new", methods=["GET", "POST"])
    @login_required
    def admin_news_create():
        form = NewsForm()
        if form.validate_on_submit():
            news = News()
            _update_news_from_form(news, form)
            db.session.add(news)
            db.session.commit()
            flash("お知らせを公開しました", "success")
            return redirect(url_for("admin_news"))
        return render_template("admin_news_form.html", form=form, is_edit=False)

    @app.route("/admin/news/<int:news_id>/edit", methods=["GET", "POST"])
    @login_required
    def admin_news_edit(news_id: int):
        news = News.query.get_or_404(news_id)
        form = NewsForm(obj=news)
        if form.validate_on_submit():
            _update_news_from_form(news, form)
            db.session.commit()
            flash("お知らせを更新しました", "success")
            return redirect(url_for("admin_news"))
        return render_template("admin_news_form.html", form=form, is_edit=True, news_item=news)

    @app.route("/admin/news/<int:news_id>/delete", methods=["POST"])
    @login_required
    def admin_news_delete(news_id: int):
        news = News.query.get_or_404(news_id)
        db.session.delete(news)
        db.session.commit()
        flash("お知らせを削除しました", "info")
        return redirect(url_for("admin_news"))

    @app.route("/admin/contact-content", methods=["GET", "POST"])
    @login_required
    def admin_contact_content():
        content = SiteContent.query.filter_by(key="contact").first()
        if not content:
            content = SiteContent(
                key="contact",
                heading_ja="お問い合わせ",
                heading_en="Contact",
                heading_zh="联系我们",
                body_ja="",
                body_en="",
                body_zh="",
                extra={},
            )
            db.session.add(content)
            db.session.flush()

        _normalize_contact_extra(content)

        form = ContactContentForm(obj=content)
        extra = content.extra or {}
        addresses = extra.get("address", {})
        if request.method == "GET":
            form.address_ja.data = addresses.get("ja", "")
            form.address_en.data = addresses.get("en", "")
            form.address_zh.data = addresses.get("zh", "")
            form.phone.data = extra.get("phone", "")
            form.email.data = extra.get("email", "")
            form.wechat_qr.data = extra.get("wechat_qr", "")

        if form.validate_on_submit():
            content.heading_ja = form.heading_ja.data
            content.heading_en = form.heading_en.data
            content.heading_zh = form.heading_zh.data
            content.body_ja = form.body_ja.data
            content.body_en = form.body_en.data
            content.body_zh = form.body_zh.data
            content.extra = {
                "address": {
                    "ja": form.address_ja.data,
                    "en": form.address_en.data,
                    "zh": form.address_zh.data,
                },
                "phone": form.phone.data,
                "email": form.email.data,
                "wechat_qr": form.wechat_qr.data,
            }
            db.session.commit()
            flash("お問い合わせ情報を更新しました", "success")
            return redirect(url_for("admin_contact_content"))

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return render_template("admin_contact_content_partial.html", form=form)
        else:
            return redirect(url_for("admin_dashboard"))

    @app.route("/admin/home-content", methods=["GET", "POST"])
    @login_required
    def admin_home_content():
        import json
        import os

        json_file_path = os.path.join(app.static_folder, "data", "home_content.json")
        existing_data: dict[str, object] = {}

        if os.path.exists(json_file_path):
            try:
                with open(json_file_path, "r", encoding="utf-8") as fp:
                    existing_data = json.load(fp) or {}
            except json.JSONDecodeError:
                # 文件存在但内容损坏时，保持空结构，允许管理员重建。
                existing_data = {}

        json_payload = json.dumps(existing_data, ensure_ascii=False, indent=2) if existing_data else "{}"
        is_ajax = request.headers.get("X-Requested-With") == "XMLHttpRequest"

        def render_home_editor(json_content: str, flash_message: str | None = None, flash_type: str | None = None, status_code: int = 200):
            template = "admin_home_content_partial.html" if is_ajax else "admin_home_content.html"
            context = {"json_content": json_content}
            if is_ajax and flash_message:
                context.update({"flash_message": flash_message, "flash_type": flash_type})
            rendered = render_template(template, **context)
            return (rendered, status_code) if status_code != 200 else rendered

        if request.method == "POST":
            json_content = (request.form.get("json_content", "") or "").strip()
            if not json_content:
                error_msg = "JSON内容を入力してください。"
                flash(error_msg, "error")
                return render_home_editor("{}" if not json_payload else json_payload, error_msg, "error", status_code=400)

            try:
                parsed_data = json.loads(json_content)
            except json.JSONDecodeError as exc:
                error_msg = f"JSON形式エラー: {exc}"
                flash(error_msg, "error")
                return render_home_editor(json_content or json_payload, error_msg, "error", status_code=400)
            except Exception as exc:  # pragma: no cover - unexpected failure surface
                error_msg = f"エラーが発生しました: {exc}"
                flash(error_msg, "error")
                app.logger.exception("Failed to save home content JSON")
                return render_home_editor(json_content or json_payload, error_msg, "error", status_code=500)

            try:
                with open(json_file_path, "w", encoding="utf-8") as fp:
                    json.dump(parsed_data, fp, ensure_ascii=False, indent=2)
            except Exception as exc:  # pragma: no cover - filesystem errors
                error_msg = f"ファイル保存に失敗しました: {exc}"
                flash(error_msg, "error")
                app.logger.exception("Failed to write home content JSON")
                return render_home_editor(json_content, error_msg, "error", status_code=500)

            success_msg = "トップページの内容を更新しました"
            flash(success_msg, "success")
            updated_payload = json.dumps(parsed_data, ensure_ascii=False, indent=2)
            return render_home_editor(updated_payload, success_msg, "success")

        return render_home_editor(json_payload)
    @app.route("/admin/messages", methods=["GET", "POST"])
    @login_required
    def admin_messages():
        if request.method == "POST":
            message_id = request.form.get("message_id", type=int)
            if message_id:
                message = Message.query.get_or_404(message_id)
                db.session.delete(message)
                db.session.commit()
                flash("メッセージを削除しました", "info")
            return redirect(url_for("admin_messages"))

        messages = Message.query.order_by(Message.created_at.desc()).all()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return render_template("admin_messages_partial.html", messages=messages)
        else:
            return redirect(url_for("admin_dashboard"))

    @app.route("/admin/users", methods=["GET", "POST"])
    @login_required
    def admin_users():
        add_user_form = UserManagementForm()
        change_password_form = ChangePasswordForm()
        users = app.load_users()
        
        if request.method == "POST":
            if add_user_form.validate_on_submit():
                username = add_user_form.username.data
                password = add_user_form.password.data
                
                if app.add_user_to_json(username, password):
                    flash(f"ユーザー '{username}' を追加しました", "success")
                else:
                    flash(f"ユーザー '{username}' は既に存在します", "error")
                return redirect(url_for("admin_users"))
            
            elif change_password_form.validate_on_submit():
                username = change_password_form.username.data
                new_password = change_password_form.new_password.data
                
                if app.update_user_password(username, new_password):
                    flash(f"ユーザー '{username}' のパスワードを変更しました", "success")
                else:
                    flash(f"ユーザー '{username}' は存在しません", "error")
                return redirect(url_for("admin_users"))
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return render_template(
                "admin_users_partial.html",
                add_user_form=add_user_form,
                change_password_form=change_password_form,
                users=users,
            )
        return render_template(
            "admin_users.html",
            add_user_form=add_user_form,
            change_password_form=change_password_form,
            users=users,
        )

    @app.route("/admin/users/delete", methods=["POST"])
    @login_required
    def admin_delete_user():
        username = request.form.get("username")
        if username:
            if app.delete_user_from_json(username):
                flash(f"ユーザー '{username}' を削除しました", "success")
            else:
                flash(f"ユーザー '{username}' の削除に失敗しました", "error")
        return redirect(url_for("admin_users"))

    class RestoreBackupForm(FlaskForm):
        backup_file = FileField("バックアップファイル", validators=[DataRequired()])

    @app.route("/admin/backup/restore", methods=["POST"])
    @login_required
    def admin_restore():
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        form = RestoreBackupForm()
        if not form.validate_on_submit():
            message = "バックアップファイルを選択してください"
            if is_ajax:
                return jsonify(status="error", message=message), 400
            flash(message, "error")
            return redirect(url_for("admin_dashboard"))

        backup: FileStorage | None = form.backup_file.data
        if not backup:
            message = "バックアップファイルを選択してください"
            if is_ajax:
                return jsonify(status="error", message=message), 400
            flash(message, "error")
            return redirect(url_for("admin_dashboard"))

        filename = secure_filename(backup.filename)
        if not filename.lower().endswith(".sql"):
            message = "SQLファイルのみアップロードできます"
            if is_ajax:
                return jsonify(status="error", message=message), 400
            flash(message, "error")
            return redirect(url_for("admin_dashboard"))

        temp_dir = tempfile.mkdtemp()
        temp_path = os.path.join(temp_dir, filename)
        backup.save(temp_path)

        db_path = "db.db"
        if not os.path.exists(db_path):
            message = "データベースファイルが存在しません"
            if is_ajax:
                return jsonify(status="error", message=message), 500
            flash(message, "error")
            return redirect(url_for("admin_dashboard"))

        success = False
        message = ""
        backup_ts: datetime | None = None

        try:
            subprocess.run(["sqlite3", db_path, f".read {temp_path}"], check=True)
            backup_ts = datetime.now()
            backup_dir = "backups"
            os.makedirs(backup_dir, exist_ok=True)
            latest_path = os.path.join(backup_dir, "latest.sql")
            shutil.copy(temp_path, latest_path)
            os.utime(latest_path, None)
            message = "バックアップをインポートしました"
            success = True
        except Exception as exc:  # pragma: no cover
            app.logger.exception("Failed to restore backup")
            message = f"バックアップのインポートに失敗しました: {exc}"
        finally:
            try:
                os.remove(temp_path)
                os.rmdir(temp_dir)
            except OSError:
                pass

        if is_ajax:
            if success:
                return jsonify(
                    status="ok",
                    message=message,
                    timestamp=backup_ts.isoformat() if backup_ts else None,
                )
            return jsonify(status="error", message=message), 500

        flash(message, "success" if success else "error")
        return redirect(url_for("admin_dashboard"))

    def cleanup_old_backups(backup_dir, max_backups=10):
        """清理旧的备份文件，只保留最新的10个"""
        try:
            backup_files = []
            for filename in os.listdir(backup_dir):
                if filename.startswith("guesthouse_backup_") and filename.endswith(".sql"):
                    file_path = os.path.join(backup_dir, filename)
                    file_stat = os.stat(file_path)
                    backup_files.append((file_path, file_stat.st_mtime))
            
            # 按修改时间排序，最新的在前
            backup_files.sort(key=lambda x: x[1], reverse=True)
            
            # 删除超过限制的旧备份
            if len(backup_files) > max_backups:
                for file_path, _ in backup_files[max_backups:]:
                    try:
                        os.remove(file_path)
                        app.logger.info(f"Deleted old backup: {file_path}")
                    except OSError as e:
                        app.logger.warning(f"Failed to delete old backup {file_path}: {e}")
                        
        except Exception as e:
            app.logger.warning(f"Failed to cleanup old backups: {e}")

    @app.route("/admin/backup")
    @login_required
    def admin_backup():
        """导出数据库为SQL文件并保存到服务器"""
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

        try:
            # 获取数据库文件路径
            db_path = "db.db"
            
            if not os.path.exists(db_path):
                message = "データベースファイルが存在しません"
                if is_ajax:
                    return jsonify(status="error", message=message), 500
                flash(message, "error")
                return redirect(url_for("admin_dashboard"))
            
            # 创建备份目录
            backup_dir = "backups"
            os.makedirs(backup_dir, exist_ok=True)
            
            # 生成备份文件名（包含时间戳）
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"guesthouse_backup_{timestamp}.sql"
            backup_path = os.path.join(backup_dir, backup_filename)
            
            # 使用sqlite3命令导出数据库
            try:
                # 尝试使用sqlite3命令行工具
                result = subprocess.run([
                    'sqlite3', db_path, '.dump'
                ], capture_output=True, text=True, check=True)
                
                # 将输出写入备份文件
                with open(backup_path, 'w', encoding='utf-8') as f:
                    f.write(result.stdout)
                
            except (subprocess.CalledProcessError, FileNotFoundError):
                # 如果sqlite3命令不可用，使用SQLAlchemy手动导出
                with open(backup_path, 'w', encoding='utf-8') as f:
                    f.write("-- 数据库备份文件\n")
                    f.write(f"-- 导出时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write("-- 数据库: guesthouse.db\n\n")
                    
                    # 导出表结构
                    f.write("PRAGMA foreign_keys=OFF;\n")
                    f.write("BEGIN TRANSACTION;\n\n")
                    
                    # 获取所有表
                    inspector = inspect(db.engine)
                    tables = inspector.get_table_names()
                    
                    for table in tables:
                        # 导出表结构
                        f.write(f"-- 表结构: {table}\n")
                        f.write(f"CREATE TABLE IF NOT EXISTS `{table}` (\n")
                        
                        columns = inspector.get_columns(table)
                        column_definitions = []
                        for column in columns:
                            col_def = f"  `{column['name']}` {column['type']}"
                            if not column['nullable']:
                                col_def += " NOT NULL"
                            if column.get('default') is not None:
                                col_def += f" DEFAULT {column['default']}"
                            if column.get('primary_key'):
                                col_def += " PRIMARY KEY"
                            column_definitions.append(col_def)
                        
                        f.write(",\n".join(column_definitions))
                        f.write("\n);\n\n")
                        
                        # 导出表数据
                        f.write(f"-- 表数据: {table}\n")
                        result = db.session.execute(text(f"SELECT * FROM `{table}`"))
                        rows = result.fetchall()
                        
                        if rows:
                            # 获取列名
                            columns = [desc[0] for desc in result.description]
                            
                            for row in rows:
                                values = []
                                for value in row:
                                    if value is None:
                                        values.append("NULL")
                                    elif isinstance(value, str):
                                        # 转义单引号
                                        escaped_value = value.replace("'", "''")
                                        values.append(f"'{escaped_value}'")
                                    else:
                                        values.append(str(value))
                                
                                f.write(f"INSERT INTO `{table}` (`{'`, `'.join(columns)}`) VALUES ({', '.join(values)});\n")
                        f.write("\n")
                    
                    f.write("COMMIT;\n")
                    f.write("PRAGMA foreign_keys=ON;\n")
            
            # 清理旧的备份文件（只保留最新的10个）
            cleanup_old_backups(backup_dir)
            
            # 记录备份时间
            backup_timestamp = datetime.now()
            
            # 返回成功响应
            message = f"バックアップが正常に作成されました: {backup_filename}"
            
            if is_ajax:
                return jsonify(
                    status="ok",
                    message=message,
                    filename=backup_filename,
                    timestamp=backup_timestamp.isoformat()
                )
            
            flash(message, "success")
            return redirect(url_for("admin_dashboard"))
            
        except Exception as e:
            message = f"バックアップエクスポートに失敗しました: {str(e)}"
            if is_ajax:
                return jsonify(status="error", message=message), 500
            flash(message, "error")
            return redirect(url_for("admin_dashboard"))

    @app.route("/admin/backup/download/<filename>")
    @login_required
    def download_backup(filename):
        """下载指定的备份文件"""
        try:
            backup_dir = "backups"
            file_path = os.path.join(backup_dir, filename)
            
            # 安全检查：确保文件在备份目录内
            if not os.path.exists(file_path) or not file_path.startswith(backup_dir):
                flash("バックアップファイルが見つかりません", "error")
                return redirect(url_for("admin_dashboard"))
            
            return send_file(file_path, as_attachment=True, download_name=filename)
            
        except Exception as e:
            flash(f"ファイルのダウンロードに失敗しました: {str(e)}", "error")
            return redirect(url_for("admin_dashboard"))


    @app.route("/admin/backup/list")
    @login_required
    def list_backups():
        """获取备份文件列表"""
        try:
            backup_dir = "backups"
            if not os.path.exists(backup_dir):
                return jsonify(backups=[])
            
            backup_files = []
            for filename in os.listdir(backup_dir):
                if filename.startswith("guesthouse_backup_") and filename.endswith(".sql"):
                    file_path = os.path.join(backup_dir, filename)
                    file_stat = os.stat(file_path)
                    backup_files.append({
                        "filename": filename,
                        "size": file_stat.st_size,
                        "created": datetime.fromtimestamp(file_stat.st_mtime).isoformat(),
                        "size_formatted": format_file_size(file_stat.st_size)
                    })
            
            # 按创建时间排序，最新的在前
            backup_files.sort(key=lambda x: x["created"], reverse=True)
            
            return jsonify(backups=backup_files)
            
        except Exception as e:
            return jsonify(error=str(e)), 500

    def format_file_size(size_bytes):
        """格式化文件大小"""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        
        return f"{size_bytes:.1f} {size_names[i]}"

    def get_latest_backup_time():
        """获取最新备份时间"""
        try:
            backup_dir = "backups"
            if not os.path.exists(backup_dir):
                return None
            
            latest_time = None
            for filename in os.listdir(backup_dir):
                if filename.startswith("guesthouse_backup_") and filename.endswith(".sql"):
                    file_path = os.path.join(backup_dir, filename)
                    file_stat = os.stat(file_path)
                    if latest_time is None or file_stat.st_mtime > latest_time:
                        latest_time = file_stat.st_mtime
            
            return datetime.fromtimestamp(latest_time) if latest_time else None
            
        except Exception:
            return None

    # 404错误处理
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('404.html'), 404
    
    # 500错误处理
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('500.html'), 500

    # 腾讯验证文件 - 写死路由
    @app.route("/tencent9183081876022215902.txt")
    def tencent_verification():
        """提供腾讯验证文件"""
        try:
            file_path = "tencent9183081876022215902.txt"
            if os.path.exists(file_path):
                return send_file(file_path, mimetype='text/plain')
            else:
                return "文件不存在", 404
        except Exception as e:
            return f"文件读取错误: {str(e)}", 500

    return app


app = create_app()


if __name__ == "__main__":
    import os
    import sys
    import socket

    port = 5050

    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print(f"错误：端口号 '{sys.argv[1]}' 不是有效的数字")
            print("使用方法：python app.py [端口号]")
            print("例如：python app.py 8080")
            sys.exit(1)
    elif os.getenv("FLASK_PORT"):
        try:
            port = int(os.getenv("FLASK_PORT"))
        except ValueError:
            print(f"错误：环境变量 FLASK_PORT='{os.getenv('FLASK_PORT')}' 不是有效的数字")
            sys.exit(1)

    is_reloader_child = os.environ.get("WERKZEUG_RUN_MAIN") == "true"

    if not is_reloader_child:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.bind(("0.0.0.0", port))
        except OSError:
            print(f"错误：端口 {port} 已被占用")
            print("请尝试其他端口，例如：python app.py 8080")
            sys.exit(1)

        print(f"启动Flask应用，端口：{port}")
        print(f"访问地址：http://localhost:{port}")
        print(f"管理后台：http://localhost:{port}/admin")
        print("按 Ctrl+C 停止服务器")

    app.run(debug=True, port=port, host="0.0.0.0")
