from flask import Flask

from .routes.web import ui_bp                         # 웹 UI 블루프린트
from .routes.cases import bp as api_bp  # API 블루프린트 정의 및 엔드포인트 로드

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
    app.register_blueprint(api_bp)                       # 케이스 API(목록·상세)
    # 이미 위에서 등록했으므로 여기서는 모듈 초기화 목적만
    app.register_blueprint(ui_bp)                         # “/” 루트 담당

    # -------------------- 워처 시작 ----------------------
    start_watcher(app)
    return app
