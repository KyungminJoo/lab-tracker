import os
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
import pathlib

db = SQLAlchemy()

# ----------------------------
#  케이스(의뢰) ---------------
# ----------------------------
class Case(db.Model):
    __tablename__ = 'case'
    id          = db.Column(db.Integer, primary_key=True)
    name        = db.Column(db.String(128), nullable=False)
    status      = db.Column(db.String(32), nullable=False, default='스캔->디자인')
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow,
                           onupdate=datetime.utcnow, nullable=False)

    @property
    def status_label(self) -> str:
        """현재 상태 문자열을 화살표 기호로 변환하여 반환한다."""
        return self.status.replace("->", "→")

    # files 역참조: case.files

    # ↓↓↓ 여기부터 메서드 추가 ↓↓↓
    def add_file(self, filepath: str):
        sf = ScanFile(
            case_id=self.id,
            filename=pathlib.Path(filepath).name,
            created_at=datetime.utcnow(),
        )
        db.session.add(sf)
        self.updated_at = datetime.utcnow()
        db.session.commit()
        
# ----------------------------
#  스캔 파일 ------------------
# ----------------------------
class ScanFile(db.Model):
    __tablename__ = 'scan_file'
    id         = db.Column(db.Integer, primary_key=True)        # ✅ PK!
    case_id    = db.Column(db.Integer, db.ForeignKey('case.id'), nullable=False)
    filename   = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    case = db.relationship('Case', backref='files')

    def to_dict(self):
        return {
            "id"        : self.id,
            "filename"  : self.filename,
            "created_at": self.created_at.isoformat(),
        }

# -------------------------------------------------
#  DB 초기화 헬퍼 ----------------------------------
# -------------------------------------------------
def init_db(app):
    """Flask 앱 컨텍스트에서 테이블을 모두 생성한다."""
    with app.app_context():
        db.create_all()


