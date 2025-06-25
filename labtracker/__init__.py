from .routes.cases import bp as cases_bp
from flask import Flask
from .config import Config
from .models import db, init_db
from .watcher import start_watcher

def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)

    # -------------------- 확장 초기화 --------------------
    db.init_app(app)
    with app.app_context():
        init_db(app)

    # -------------------- 블루프린트 ---------------------
    app.register_blueprint(cases_bp)                      # 케이스 목록·상세
    from .routes import bp as api_bp                      # ← 정의만 가져옴
    # ← 중복 제거: api_bp 등록 삭제
    from .routes.web import ui_bp
    app.register_blueprint(ui_bp)                         # “/” 루트 담당

    # -------------------- 워처 시작 ----------------------
    start_watcher(app)
    return app