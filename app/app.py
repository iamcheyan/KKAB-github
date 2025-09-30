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
from urllib.parse import urljoin, urlparse

try:
    from .forms import (
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
    from .json_models import (
        Room,
        Booking,
        Message,
        Admin,
        News,
        SiteContent,
        room_model,
        booking_model,
        message_model,
        news_model,
        site_content_model,
        data_manager,
    )
    from .translations import DEFAULT_LANGUAGE, LANGUAGES, TRANSLATIONS
except ImportError:
    # 允许以 "python app/app.py" 直接执行
    import sys as _sys
    import os as _os
    _parent = _os.path.dirname(_os.path.dirname(__file__))
    if _parent not in _sys.path:
        _sys.path.insert(0, _parent)
    from app.forms import (
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
    from app.json_models import (
        Room,
        Booking,
        Message,
        Admin,
        News,
        SiteContent,
        room_model,
        booking_model,
        message_model,
        news_model,
        site_content_model,
        data_manager,
    )
    from app.translations import DEFAULT_LANGUAGE, LANGUAGES, TRANSLATIONS


csrf = CSRFProtect()


def create_app() -> Flask:
    """Application factory configuring Flask and login."""
    app = Flask(__name__, template_folder='templates', static_folder='static')
    app.config.update(
        SECRET_KEY=os.environ.get("SECRET_KEY", "dev-secret-key"),
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
        users_file_path = os.path.join(os.path.dirname(__file__), 'users.json')
        if os.path.exists(users_file_path):
            with open(users_file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []

    def save_users(users):
        import json
        users_file_path = os.path.join(os.path.dirname(__file__), 'users.json')
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
    
    # 关函数をアプリケーションコンテキストに追加
    app.load_home_content = load_home_content
    app.load_users = load_users
    app.add_user_to_json = add_user_to_json
    app.update_user_password = update_user_password
    app.delete_user_from_json = delete_user_from_json

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
        
        # Handle dictionary objects (from JSON models)
        if isinstance(model, dict):
            value = model.get(attr_name)
            if value:
                return value
            fallback = model.get(base)
            if fallback:
                return fallback
            default_attr = f"{base}_{DEFAULT_LANGUAGE}"
            return model.get(default_attr, "")
        
        # Handle object attributes (legacy support)
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

    def _generate_static_site() -> None:
        """生成静态站点到项目根目录，静态资源前缀重写为 app/static/。

        参考 veikin.com：为多语言与房间详情生成页面，便于 GitHub Pages 部署。
        """
        try:
            project_root = os.path.dirname(os.path.dirname(__file__))
            os.makedirs(project_root, exist_ok=True)

            def _write_html(route: str, out_rel_path: str, duplicate_html: bool = True) -> None:
                # 目录式输出：如果 out_rel_path 以 '/' 结尾或不含扩展名，则写入 path/index.html
                # 另外可选生成同名 .html 以便直接访问文件
                target_dir = os.path.join(project_root, out_rel_path)
                # 判定是否为目录式
                if out_rel_path.endswith('/') or not os.path.splitext(out_rel_path)[1]:
                    out_dir = target_dir.rstrip('/')
                    os.makedirs(out_dir, exist_ok=True)
                    file_path_primary = os.path.join(out_dir, 'index.html')
                    file_path_alias = (out_dir + '.html') if duplicate_html else None
                else:
                    os.makedirs(os.path.dirname(target_dir), exist_ok=True)
                    file_path_primary = target_dir
                    file_path_alias = None
                with app.test_client() as client:
                    resp = client.get(route)
                    if resp.status_code != 200:
                        return
                    html = resp.get_data(as_text=True)
                    # 将 Flask 的 /static/ 路径重写为根级 /app/static/，避免子目录相对路径问题
                    html = html.replace('"/static/', '"/app/static/').replace("'/static/", "'/app/static/")
                    # 语言切换链接重写：/lang/<code>?next=/[cur]/rest -> /<code>/rest
                    import re
                    def _rewrite(m):
                        quote = m.group(1)
                        target = m.group(2)
                        next_path = m.group(3) or ""
                        # 去掉现有语言前缀
                        for lg in LANGUAGES:
                            if next_path.startswith(lg + "/"):
                                next_path = next_path[len(lg)+1:]
                                break
                        if next_path and not next_path.endswith('/') and not next_path.split('#')[0].split('?')[0].endswith('.html'):
                            # 保持目录式，若为空则只返回 /<target>/
                            pass
                        return f"{quote}/{target}/" + next_path
                    html = re.sub(r"([\"\'])/lang/([a-zA-Z\-]{2,})\?next=/([^\"\']*)", _rewrite, html)
                with open(file_path_primary, 'w', encoding='utf-8') as f:
                    f.write(html)
                if file_path_alias:
                    # 兼容形式，例如 rooms/index.html 同时生成 rooms.html
                    with open(file_path_alias, 'w', encoding='utf-8') as f:
                        f.write(html)

            # 基础页面
            _write_html('/', 'index.html')
            _write_html('/rooms', 'rooms/')
            _write_html('/contact', 'contact/')
            _write_html('/management', 'management/')

            # 多语言首页/页面
            for lang in LANGUAGES:
                _write_html(f'/{lang}/', os.path.join(lang, 'index.html'))
                _write_html(f'/{lang}/rooms', os.path.join(lang, 'rooms/'))
                _write_html(f'/{lang}/contact', os.path.join(lang, 'contact/'))
                _write_html(f'/{lang}/management', os.path.join(lang, 'management/'))

            # 房间详情页面（含多语言）
            try:
                rooms = room_model.get_all()
            except Exception:
                rooms = []
            for room in rooms:
                rid = room.get('id')
                if not rid:
                    continue
                _write_html(f'/rooms/{rid}', os.path.join('rooms', f'{rid}/'))
                for lang in LANGUAGES:
                    _write_html(f'/{lang}/rooms/{rid}', os.path.join(lang, 'rooms', f'{rid}/'))

            print("[static] 静态页已生成到项目根目录（静态资源前缀 app/static/）")
        except Exception as e:
            # 生成失败不影响运行
            print(f"[static] 生成静态页失败: {e}")

    # 确保JSON数据目录存在
    with app.app_context():
        data_dir = data_manager.data_dir
        if not os.path.exists(data_dir):
            print(f"创建数据目录: {data_dir}")
            os.makedirs(data_dir, exist_ok=True)
        
        print(f"使用JSON文件存储数据，数据目录: {os.path.abspath(data_dir)}")
        
        # 检查必要的JSON文件是否存在
        required_files = ['rooms.json', 'bookings.json', 'messages.json', 'admins.json', 'news.json', 'site_content.json']
        missing_files = []
        
        for filename in required_files:
            file_path = os.path.join(data_dir, filename)
            if not os.path.exists(file_path):
                missing_files.append(filename)
        
        if missing_files:
            print(f"警告：缺少以下JSON数据文件: {', '.join(missing_files)}")
            print("如果这是首次运行，请先运行数据迁移脚本: python3 migrate_data.py")
            # 创建空的JSON文件以避免错误
            for filename in missing_files:
                file_path = os.path.join(data_dir, filename)
                with open(file_path, 'w', encoding='utf-8') as f:
                    import json
                    json.dump([], f)
                print(f"创建空的数据文件: {filename}")
        else:
            print("所有JSON数据文件已就绪")

        # 检查数据状态
        room_count = len(room_model.get_all())
        admin_count = len(Admin.get_all(data_manager))
        print(f"数据状态：{room_count} 个房间，{admin_count} 个管理员账户")
        
        if admin_count == 0:
            print("警告：没有管理员账户，请通过管理界面创建管理员账户")

    login_manager = LoginManager(app)
    login_manager.login_view = "admin_login"

    @login_manager.user_loader
    def load_user(user_id: str):
        return Admin.get_by_id(data_manager, int(user_id))

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
                _home_cache["content"] = site_content_model.get_by_key("home")
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

        updated = False

        # 同时兼容 dict（JSON记录）与具有属性的对象两种形式
        if isinstance(content, dict):
            extra = dict(content.get("extra") or {})

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
                content["extra"] = extra
                content_id = content.get("id")
                if content_id is not None:
                    # 将修正写回存储
                    site_content_model.update(content_id, extra=extra)
        else:
            # 对象形式：访问属性并调用保存方法
            try:
                extra = dict(getattr(content, "extra", {}) or {})
            except Exception:
                extra = {}

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
                try:
                    content.extra = extra
                    # 若对象有 save 方法则持久化
                    if hasattr(content, "save") and callable(getattr(content, "save")):
                        content.save()
                except Exception:
                    pass

    @app.route("/")
    def index():
        # Show a curated list of rooms and general description.
        featured_rooms = room_model.get_all()[:3]  # 获取前3个房间
        news_items = [news for news in news_model.get_all() if news.get('is_published', True)]
        news_items.sort(key=lambda x: x.get('published_at', ''), reverse=True)
        news_items = news_items[:4]  # 获取前4个新闻
        home_content = app.load_home_content()
        return render_template("index.html", rooms=featured_rooms, news_items=news_items, home_content=home_content)

    @app.route("/<locale>/")
    def index_with_locale(locale: str):
        if locale in LANGUAGES:
            session["locale"] = locale
        featured_rooms = room_model.get_all()[:3]  # 获取前3个房间
        news_items = [news for news in news_model.get_all() if news.get('is_published', True)]
        news_items.sort(key=lambda x: x.get('published_at', ''), reverse=True)
        news_items = news_items[:4]  # 获取前4个新闻
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
        all_rooms = room_model.get_all()
        return render_template("rooms.html", rooms=all_rooms)

    @app.route("/<locale>/rooms")
    def rooms_with_locale(locale: str):
        if locale in LANGUAGES:
            session["locale"] = locale
        all_rooms = room_model.get_all()
        return render_template("rooms.html", rooms=all_rooms)

    @app.route("/rooms/<int:room_id>")
    def room_detail(room_id: int):
        room = room_model.get_by_id(room_id)
        if not room:
            from flask import abort
            abort(404)
        # 获取其他房间作为推荐房源（排除当前房间）
        all_rooms = room_model.get_all()
        recommended_rooms = [r for r in all_rooms if r.get('id') != room_id][:3]
        return render_template("room_detail.html", room=room, recommended_rooms=recommended_rooms)

    @app.route("/<locale>/rooms/<int:room_id>")
    def room_detail_with_locale(locale: str, room_id: int):
        if locale in LANGUAGES:
            session["locale"] = locale
        room = room_model.get_by_id(room_id)
        if not room:
            from flask import abort
            abort(404)
        # 获取其他房间作为推荐房源（排除当前房间）
        all_rooms = room_model.get_all()
        recommended_rooms = [r for r in all_rooms if r.get('id') != room_id][:3]
        return render_template("room_detail.html", room=room, recommended_rooms=recommended_rooms)

    @app.route("/booking")
    def booking():
        return redirect("https://www.airbnb.com/s?query=Kyoto", code=302)

    @app.route("/booking/success/<int:booking_id>")
    def booking_success(booking_id: int):
        booking_record = Booking.get_by_id(booking_id)
        if not booking_record:
            from flask import abort
            abort(404)
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
            message.save()
            flash(translate("contact.flash.success"), "success")
            return redirect(url_for("contact"))
        
        # 获取联系信息内容
        contact_content = site_content_model.get_by_key("contact")
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
            message.save()
            flash(translate("contact.flash.success"), "success")
            return redirect(url_for("contact_with_locale", locale=locale))
        
        # 获取联系信息内容
        contact_content = site_content_model.get_by_key("contact")
        _normalize_contact_extra(contact_content)
        return render_template("contact.html", form=form, contact_content=contact_content)

    @app.route("/admin/login", methods=["GET", "POST"])
    def admin_login():
        if current_user.is_authenticated:
            return redirect(url_for("admin_dashboard"))
        form = LoginForm()
        if form.validate_on_submit():
            admin = Admin.get_by_username(data_manager, form.username.data)
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
        messages_count = len(message_model.get_all())
        news_count = len(news_model.get_all())
        room_count = len(room_model.get_all())
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
        rooms = room_model.get_all()
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
                # Handle image upload
                image_path = None
                if form.image_file.data:
                    # Generate a temporary ID for the image filename
                    temp_id = str(uuid.uuid4())
                    image_path = _save_uploaded_file(form.image_file.data, temp_id)
                else:
                    image_path = form.image.data

                room_data = {
                    'name_ja': form.name_ja.data,
                    'name_en': form.name_en.data,
                    'name_zh': form.name_zh.data,
                    'description_ja': form.description_ja.data,
                    'description_en': form.description_en.data,
                    'description_zh': form.description_zh.data,
                    'price': form.price.data,
                    'capacity': form.capacity.data,
                    'address_ja': form.address_ja.data,
                    'address_en': form.address_en.data,
                    'address_zh': form.address_zh.data,
                    'permit_number': form.permit_number.data,
                    'image': image_path,
                    'airbnb_url': form.airbnb_url.data,
                    'name': form.name_ja.data,  # Legacy field
                    'description': form.description_ja.data,  # Legacy field
                }
                room_model.create(**room_data)
                flash("客室を作成しました", "success")
                return redirect(url_for("admin_rooms"))
            except Exception as e:
                flash(f"作成中にエラーが発生しました: {str(e)}", "error")
        return render_template("admin_room_form.html", form=form, is_edit=False)

    @app.route("/admin/rooms/<int:room_id>/edit", methods=["GET", "POST"])
    @login_required
    def admin_room_edit(room_id: int):
        room = room_model.get_by_id(room_id)
        if not room:
            from flask import abort
            abort(404)
        form = RoomAdminForm(obj=room)
        if form.validate_on_submit():
            try:
                # Handle image upload
                image_path = None
                if form.image_file.data:
                    image_path = _save_uploaded_file(form.image_file.data, room_id)
                else:
                    image_path = form.image.data

                update_data = {
                    'name_ja': form.name_ja.data,
                    'name_en': form.name_en.data,
                    'name_zh': form.name_zh.data,
                    'description_ja': form.description_ja.data,
                    'description_en': form.description_en.data,
                    'description_zh': form.description_zh.data,
                    'price': form.price.data,
                    'capacity': form.capacity.data,
                    'address_ja': form.address_ja.data,
                    'address_en': form.address_en.data,
                    'address_zh': form.address_zh.data,
                    'permit_number': form.permit_number.data,
                    'image': image_path,
                    'airbnb_url': form.airbnb_url.data,
                    'name': form.name_ja.data,  # Legacy field
                    'description': form.description_ja.data,  # Legacy field
                }
                room_model.update(room_id, **update_data)
                flash("客室情報を更新しました", "success")
                return redirect(url_for("admin_rooms"))
            except Exception as e:
                flash(f"更新中にエラーが発生しました: {str(e)}", "error")
        return render_template("admin_room_form.html", form=form, is_edit=True, room=room)

    @app.route("/admin/rooms/<int:room_id>/delete", methods=["POST"])
    @login_required
    def admin_room_delete(room_id: int):
        room = room_model.get_by_id(room_id)
        if not room:
            from flask import abort
            abort(404)
        room.delete()
        flash("客室を削除しました", "info")
        return redirect(url_for("admin_rooms"))

    @app.route("/admin/news")
    @login_required
    def admin_news():
        news_items = news_model.get_all()
        news_items.sort(key=lambda x: x.get('published_at', ''), reverse=True)
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return render_template("admin_news_partial.html", news_items=news_items)
        else:
            return redirect(url_for("admin_dashboard"))

    @app.route("/admin/news/new", methods=["GET", "POST"])
    @login_required
    def admin_news_create():
        form = NewsForm()
        if form.validate_on_submit():
            news_data = {
                'title_ja': form.title_ja.data,
                'title_en': form.title_en.data,
                'title_zh': form.title_zh.data,
                'body_ja': form.body_ja.data,
                'body_en': form.body_en.data,
                'body_zh': form.body_zh.data,
                'is_published': form.is_published.data,
            }
            news_model.create(**news_data)
            flash("お知らせを公開しました", "success")
            return redirect(url_for("admin_news"))
        return render_template("admin_news_form.html", form=form, is_edit=False)

    @app.route("/admin/news/<int:news_id>/edit", methods=["GET", "POST"])
    @login_required
    def admin_news_edit(news_id: int):
        news = news_model.get_by_id(news_id)
        if not news:
            from flask import abort
            abort(404)
        form = NewsForm(obj=news)
        if form.validate_on_submit():
            update_data = {
                'title_ja': form.title_ja.data,
                'title_en': form.title_en.data,
                'title_zh': form.title_zh.data,
                'body_ja': form.body_ja.data,
                'body_en': form.body_en.data,
                'body_zh': form.body_zh.data,
                'is_published': form.is_published.data,
            }
            news_model.update(news_id, **update_data)
            flash("お知らせを更新しました", "success")
            return redirect(url_for("admin_news"))
        return render_template("admin_news_form.html", form=form, is_edit=True, news_item=news)

    @app.route("/admin/news/<int:news_id>/delete", methods=["POST"])
    @login_required
    def admin_news_delete(news_id: int):
        news = news_model.get_by_id(news_id)
        if not news:
            from flask import abort
            abort(404)
        news.delete()
        flash("お知らせを削除しました", "info")
        return redirect(url_for("admin_news"))

    @app.route("/admin/contact-content", methods=["GET", "POST"])
    @login_required
    def admin_contact_content():
        content = site_content_model.get_by_key("contact")
        if not content:
            content = site_content_model.create(
                key="contact",
                heading_ja="お問い合わせ",
                heading_en="Contact",
                heading_zh="联系我们",
                body_ja="",
                body_en="",
                body_zh="",
                extra={},
            )

        _normalize_contact_extra(content)

        form = ContactContentForm()
        extra = content.get('extra', {})
        addresses = extra.get("address", {})
        if request.method == "GET":
            form.heading_ja.data = content.get('heading_ja', '')
            form.heading_en.data = content.get('heading_en', '')
            form.heading_zh.data = content.get('heading_zh', '')
            form.body_ja.data = content.get('body_ja', '')
            form.body_en.data = content.get('body_en', '')
            form.body_zh.data = content.get('body_zh', '')
            form.address_ja.data = addresses.get("ja", "")
            form.address_en.data = addresses.get("en", "")
            form.address_zh.data = addresses.get("zh", "")
            form.phone.data = extra.get("phone", "")
            form.email.data = extra.get("email", "")
            form.wechat_qr.data = extra.get("wechat_qr", "")

        if form.validate_on_submit():
            update_data = {
                'heading_ja': form.heading_ja.data,
                'heading_en': form.heading_en.data,
                'heading_zh': form.heading_zh.data,
                'body_ja': form.body_ja.data,
                'body_en': form.body_en.data,
                'body_zh': form.body_zh.data,
                'extra': {
                    "address": {
                        "ja": form.address_ja.data,
                        "en": form.address_en.data,
                        "zh": form.address_zh.data,
                    },
                    "phone": form.phone.data,
                    "email": form.email.data,
                    "wechat_qr": form.wechat_qr.data,
                }
            }
            site_content_model.update(content['id'], **update_data)
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
                message = message_model.get_by_id(message_id)
                if message:
                    message.delete()
                    flash("メッセージを削除しました", "info")
                else:
                    flash("メッセージが見つかりません", "error")
            return redirect(url_for("admin_messages"))

        messages = message_model.get_all()
        # Sort by created_at descending
        messages.sort(key=lambda x: x.created_at, reverse=True)
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
        if not filename.lower().endswith((".tar.gz", ".json")):
            message = "tar.gzまたはJSONファイルのみアップロードできます"
            if is_ajax:
                return jsonify(status="error", message=message), 400
            flash(message, "error")
            return redirect(url_for("admin_dashboard"))

        temp_dir = tempfile.mkdtemp()
        temp_path = os.path.join(temp_dir, filename)
        backup.save(temp_path)

        success = False
        message = ""
        backup_ts: datetime | None = None

        try:
            import tarfile
            import json
            
            if filename.lower().endswith(".tar.gz"):
                # 处理tar.gz备份文件
                with tarfile.open(temp_path, 'r:gz') as tar:
                    tar.extractall(temp_dir)
                
                # 恢复JSON文件到data目录
                data_files = ['rooms.json', 'bookings.json', 'messages.json', 'admins.json', 'news.json', 'site_content.json', 'users.json']
                for data_file in data_files:
                    extracted_path = os.path.join(temp_dir, data_file)
                    if os.path.exists(extracted_path):
                        target_path = os.path.join(data_manager.data_dir, data_file)
                        shutil.copy2(extracted_path, target_path)
                
                # 恢复home_content.json到static/data目录
                home_content_path = os.path.join(temp_dir, 'home_content.json')
                if os.path.exists(home_content_path):
                    target_path = os.path.join('static', 'data', 'home_content.json')
                    os.makedirs(os.path.dirname(target_path), exist_ok=True)
                    shutil.copy2(home_content_path, target_path)
                    
            elif filename.lower().endswith(".json"):
                # 处理单个JSON文件
                with open(temp_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # 根据文件名确定目标位置
                if 'home_content' in filename:
                    target_path = os.path.join('static', 'data', 'home_content.json')
                    os.makedirs(os.path.dirname(target_path), exist_ok=True)
                else:
                    target_path = os.path.join(data_manager.data_dir, filename)
                
                with open(target_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
            
            backup_ts = datetime.now()
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
                if (filename.startswith("guesthouse_backup_") or filename.startswith("json_data_backup_")) and (filename.endswith(".sql") or filename.endswith(".tar.gz")):
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
        """导出JSON数据为备份文件并保存到服务器"""
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

        try:
            # 检查数据目录是否存在
            data_dir = data_manager.data_dir
            
            if not os.path.exists(data_dir):
                message = "データディレクトリが存在しません"
                if is_ajax:
                    return jsonify(status="error", message=message), 500
                flash(message, "error")
                return redirect(url_for("admin_dashboard"))
            
            # 创建备份目录
            backup_dir = os.path.join(os.path.dirname(__file__), "backups")
            os.makedirs(backup_dir, exist_ok=True)
            
            # 生成备份文件名（包含时间戳）
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"json_data_backup_{timestamp}.tar.gz"
            backup_path = os.path.join(backup_dir, backup_filename)
            
            # 创建tar.gz备份文件
            import tarfile
            with tarfile.open(backup_path, "w:gz") as tar:
                # 添加所有JSON数据文件
                json_files = [
                    "rooms.json", "bookings.json", "messages.json", 
                    "admins.json", "news.json", "site_content.json"
                ]
                
                for json_file in json_files:
                    file_path = os.path.join(data_dir, json_file)
                    if os.path.exists(file_path):
                        tar.add(file_path, arcname=json_file)
                
                # 添加用户文件和主页内容
                users_json_path = os.path.join(os.path.dirname(__file__), "users.json")
                if os.path.exists(users_json_path):
                    tar.add(users_json_path, arcname="users.json")
                
                home_content_path = os.path.join(app.static_folder, "data", "home_content.json")
                if os.path.exists(home_content_path):
                    tar.add(home_content_path, arcname="home_content.json")
            
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
            else:
                flash(message, "success")
                return redirect(url_for("admin_dashboard"))
                
        except Exception as e:
            message = f"バックアップの作成に失敗しました: {str(e)}"
            app.logger.exception("Backup creation failed")
            
            if is_ajax:
                return jsonify(status="error", message=message), 500
            else:
                flash(message, "error")
                return redirect(url_for("admin_dashboard"))

    @app.route("/admin/backup/download/<filename>")
    @login_required
    def download_backup(filename):
        """下载指定的备份文件"""
        try:
            backup_dir = os.path.join(os.path.dirname(__file__), "backups")
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
            backup_dir = os.path.join(os.path.dirname(__file__), "backups")
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
        # JSON模型不需要数据库会话回滚
        return render_template('500.html'), 500

    # 腾讯验证文件 - 写死路由
    @app.route("/tencent9183081876022215902.txt")
    def tencent_verification():
        """提供腾讯验证文件"""
        try:
            file_path = os.path.join(os.path.dirname(__file__), "tencent9183081876022215902.txt")
            if os.path.exists(file_path):
                return send_file(file_path, mimetype='text/plain')
            else:
                return "文件不存在", 404
        except Exception as e:
            return f"文件读取错误: {str(e)}", 500

    # 应用创建完成后生成一次静态页（适用于 flask run / 直接运行）
    try:
        _generate_static_site()
    except Exception:
        pass

    return app


app = create_app()


if __name__ == "__main__":
    import os
    import sys
    import socket
    import argparse

    parser = argparse.ArgumentParser(description="GuestHouse 开发服务器与静态导出")
    parser.add_argument("port", nargs="?", type=int, help="HTTP 端口号 (默认 5050)")
    parser.add_argument("--build-static", action="store_true", help="仅生成静态页后退出")
    args = parser.parse_args()

    if args.build_static or os.getenv("BUILD_STATIC") == "1":
        # 仅生成静态站点
        _ = create_app()
        print("[static] 仅生成静态站点完成 (BUILD_STATIC)")
        sys.exit(0)

    port = 5050
    if args.port is not None:
        port = args.port
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
            print("请尝试其他端口，例如：python app/app.py 8080")
            sys.exit(1)

        print(f"启动Flask应用，端口：{port}")
        print(f"访问地址：http://localhost:{port}")
        print(f"管理后台：http://localhost:{port}/admin")
        print("按 Ctrl+C 停止服务器")

    app.run(debug=True, port=port, host="0.0.0.0")
