"""WTForms definitions for the GuestHouse application."""
from datetime import date

from flask_wtf import FlaskForm
from wtforms import BooleanField, DateField, DecimalField, FileField, IntegerField, PasswordField, SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, NumberRange, Optional, URL, ValidationError
from flask_wtf.file import FileAllowed, FileSize


class BookingForm(FlaskForm):
    """Booking form allowing guests to reserve a room."""

    room = SelectField("客室タイプ", coerce=int, validators=[DataRequired(message="客室をお選びください")])
    name = StringField("お名前", validators=[DataRequired(message="お名前を入力してください"), Length(max=80)])
    email = StringField("メールアドレス", validators=[DataRequired(message="メールアドレスを入力してください"), Email(message="正しいメールアドレスを入力してください"), Length(max=120)])
    check_in = DateField("チェックイン", validators=[DataRequired(message="チェックイン日をお選びください")], format="%Y-%m-%d")
    check_out = DateField("チェックアウト", validators=[DataRequired(message="チェックアウト日をお選びください")], format="%Y-%m-%d")
    guests = IntegerField("ご利用人数", validators=[DataRequired(message="人数を入力してください"), NumberRange(min=1, message="1名以上で入力してください")])
    submit = SubmitField("送信")

    def validate_check_out(self, field):
        """Ensure the check-out date follows the check-in date."""
        if self.check_in.data and field.data and field.data <= self.check_in.data:
            raise ValidationError("チェックアウト日はチェックイン日より後の日付をお選びください")

    def validate_check_in(self, field):
        if field.data and field.data < date.today():
            raise ValidationError("本日以降の日付をお選びください")


class ContactForm(FlaskForm):
    """Contact form for guest inquiries."""

    name = StringField("お名前", validators=[DataRequired(message="お名前を入力してください"), Length(max=80)])
    email = StringField("メールアドレス", validators=[DataRequired(message="メールアドレスを入力してください"), Email(message="正しいメールアドレスを入力してください"), Length(max=120)])
    message = TextAreaField("お問い合わせ内容", validators=[DataRequired(message="メッセージをご記入ください"), Length(max=1000)])
    submit = SubmitField("送信する")


class LoginForm(FlaskForm):
    """Administrator login form."""

    username = StringField("ユーザー名", validators=[DataRequired(message="ユーザー名を入力してください")])
    password = PasswordField("パスワード", validators=[DataRequired(message="パスワードを入力してください")])
    submit = SubmitField("ログイン")


class RoomAdminForm(FlaskForm):
    """Administrator form for creating or updating rooms."""

    name_ja = StringField("客室名（日本語）", validators=[DataRequired(), Length(max=120)])
    name_en = StringField("客室名（英語）", validators=[DataRequired(), Length(max=120)])
    name_zh = StringField("客室名（中文）", validators=[DataRequired(), Length(max=120)])
    description_ja = TextAreaField("説明（日本語）", validators=[DataRequired()])
    description_en = TextAreaField("Description (English)", validators=[DataRequired()])
    description_zh = TextAreaField("介绍（中文）", validators=[DataRequired()])
    address_ja = StringField("住所（日本語）", validators=[DataRequired(), Length(max=255)])
    address_en = StringField("Address (English)", validators=[DataRequired(), Length(max=255)])
    address_zh = StringField("地址（中文）", validators=[DataRequired(), Length(max=255)])
    permit_number = StringField("許可番号", validators=[DataRequired(), Length(max=120)])
    image = StringField("メイン画像パス", validators=[DataRequired(), Length(max=200)])
    image_file = FileField("画像ファイル", validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'gif', 'avif'], '画像ファイル（JPG, PNG, GIF, AVIF）を選択してください'),
        FileSize(max_size=5*1024*1024, message='ファイルサイズは5MB以下にしてください')
    ])
    airbnb_url = StringField("Airbnb リンク", validators=[DataRequired(), URL()])
    submit = SubmitField("保存")


class NewsForm(FlaskForm):
    """Administrator form for publishing news."""

    title_ja = StringField("タイトル（日本語）", validators=[DataRequired(), Length(max=160)])
    title_en = StringField("Title (English)", validators=[DataRequired(), Length(max=160)])
    title_zh = StringField("标题（中文）", validators=[DataRequired(), Length(max=160)])
    body_ja = TextAreaField("本文（日本語）", validators=[DataRequired()])
    body_en = TextAreaField("Body (English)", validators=[DataRequired()])
    body_zh = TextAreaField("内容（中文）", validators=[DataRequired()])
    is_published = BooleanField("公開する", default=True)
    submit = SubmitField("保存")


class ContactContentForm(FlaskForm):
    """Administrator form for editable contact information."""

    heading_ja = StringField("見出し（日本語）", validators=[DataRequired(), Length(max=160)])
    heading_en = StringField("Heading (English)", validators=[DataRequired(), Length(max=160)])
    heading_zh = StringField("标题（中文）", validators=[DataRequired(), Length(max=160)])
    body_ja = TextAreaField("本文（日本語）", validators=[DataRequired()])
    body_en = TextAreaField("Body (English)", validators=[DataRequired()])
    body_zh = TextAreaField("内容（中文）", validators=[DataRequired()])
    address_ja = StringField("住所（日本語）", validators=[DataRequired()])
    address_en = StringField("Address (English)", validators=[DataRequired()])
    address_zh = StringField("地址（中文）", validators=[DataRequired()])
    phone = StringField("電話", validators=[DataRequired(), Length(max=30)])
    email = StringField("メール", validators=[DataRequired(), Email(), Length(max=120)])
    wechat_qr = StringField("WeChat QR パス", validators=[Optional(), Length(max=200)])
    submit = SubmitField("保存")


class HomeContentForm(FlaskForm):
    """Admin form for editing homepage copy in three languages."""

    # Hero
    heading_ja = StringField("ヒーロー見出し（日本語）", validators=[DataRequired(), Length(max=160)])
    heading_en = StringField("Hero Heading (English)", validators=[DataRequired(), Length(max=160)])
    heading_zh = StringField("主视觉标题（中文）", validators=[DataRequired(), Length(max=160)])
    body_ja = TextAreaField("リード文（日本語）", validators=[DataRequired()])
    body_en = TextAreaField("Lead (English)", validators=[DataRequired()])
    body_zh = TextAreaField("引导文（中文）", validators=[DataRequired()])

    kicker_ja = StringField("キッカー（日本語）", validators=[DataRequired()])
    kicker_en = StringField("Kicker (English)", validators=[DataRequired()])
    kicker_zh = StringField("引导词（中文）", validators=[DataRequired()])

    badge_ja = StringField("バッジ文言（日本語）", validators=[DataRequired()])
    badge_en = StringField("Badge (English)", validators=[DataRequired()])
    badge_zh = StringField("徽章文案（中文）", validators=[DataRequired()])

    point1_ja = StringField("ポイント1（日本語）", validators=[DataRequired()])
    point1_en = StringField("Point 1 (English)", validators=[DataRequired()])
    point1_zh = StringField("要点1（中文）", validators=[DataRequired()])
    point2_ja = StringField("ポイント2（日本語）", validators=[DataRequired()])
    point2_en = StringField("Point 2 (English)", validators=[DataRequired()])
    point2_zh = StringField("要点2（中文）", validators=[DataRequired()])
    point3_ja = StringField("ポイント3（日本語）", validators=[DataRequired()])
    point3_en = StringField("Point 3 (English)", validators=[DataRequired()])
    point3_zh = StringField("要点3（中文）", validators=[DataRequired()])

    info_hours_ja = StringField("チェックイン/アウト（日本語）", validators=[DataRequired()])
    info_hours_en = StringField("Hours (English)", validators=[DataRequired()])
    info_hours_zh = StringField("入住/退房（中文）", validators=[DataRequired()])

    info_station_ja = StringField("最寄駅（日本語）", validators=[DataRequired()])
    info_station_en = StringField("Nearest station (English)", validators=[DataRequired()])
    info_station_zh = StringField("最近车站（中文）", validators=[DataRequired()])

    cta_book_ja = StringField("予約ボタン（日本語）", validators=[DataRequired()])
    cta_book_en = StringField("CTA Book (English)", validators=[DataRequired()])
    cta_book_zh = StringField("预约按钮（中文）", validators=[DataRequired()])
    cta_rooms_ja = StringField("客室ボタン（日本語）", validators=[DataRequired()])
    cta_rooms_en = StringField("CTA Rooms (English)", validators=[DataRequired()])
    cta_rooms_zh = StringField("客房按钮（中文）", validators=[DataRequired()])

    submit = SubmitField("保存")


class UserManagementForm(FlaskForm):
    """ユーザー管理フォーム - ユーザー追加"""
    username = StringField("ユーザー名", validators=[DataRequired(message="ユーザー名を入力してください"), Length(max=80)])
    password = PasswordField("パスワード", validators=[DataRequired(message="パスワードを入力してください"), Length(min=6, message="パスワードは6文字以上で入力してください")])
    submit = SubmitField("ユーザー追加")


class ChangePasswordForm(FlaskForm):
    """パスワード変更フォーム"""
    username = StringField("ユーザー名", validators=[DataRequired(message="ユーザー名を入力してください")])
    new_password = PasswordField("新しいパスワード", validators=[DataRequired(message="新しいパスワードを入力してください"), Length(min=6, message="パスワードは6文字以上で入力してください")])
    submit = SubmitField("パスワード変更")
