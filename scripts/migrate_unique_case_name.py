from labtracker.config import Config
from labtracker.models import db
from flask import Flask

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
with app.app_context():
    # SQLite: 유니크 인덱스 추가 (존재하지 않으면)
    db.session.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS idx_case_name ON case (name)"
    )
    db.session.commit()
    print("✅ idx_case_name unique index ensured")

