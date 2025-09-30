"""App package initializer exposing the Flask application factory.

本文件使项目可以通过 `from app import create_app, app` 导入。
"""

from .app import create_app, app  # noqa: F401


