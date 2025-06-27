import os
from datetime import datetime, timezone
# 모든 시간은 UTC 기준으로 기록하기 위해 timezone.utc를 사용합니다.
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import JSONB
import pathlib

db = SQLAlchemy()

# ----------------------------
#  케이스(의뢰) ---------------
# ----------------------------
class Case(db.Model):
    __tablename__ = 'case'
    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.String(64), nullable=False, unique=True)
    patient_name = db.Column(db.String(64))
    patient_ref = db.Column(db.String(32))
    ordered_at = db.Column(db.DateTime(timezone=True))
    restoration_items = db.Column(db.JSON().with_variant(JSONB, "postgresql"))
    shade_material = db.Column(
        db.JSON().with_variant(JSONB, "postgresql")
    )
    status = db.Column(db.String(32), nullable=False, default='scan완료')
    created_at = db.Column(
        db.DateTime(timezone=True),
        server_default=db.func.now(),
    )  # UTC 타임존을 유지
    updated_at = db.Column(
        db.DateTime(timezone=True),
        server_default=db.func.now(),
        onupdate=db.func.now(),
    )  # 갱신 시에도 UTC 보존

    @property
    def status_label(self) -> str:
        """현재 상태 문자열을 화살표 기호로 변환하여 반환한다."""
        return self.status.replace("->", "→")

    # files 역참조: case.files

    # ↓↓↓ 여기부터 메서드 추가 ↓↓↓
    # datetime.utcnow() 대신 timezone.now(timezone.utc)를 사용해
    # timezone-aware 값을 저장합니다.
    def add_file(self, filepath: str):
        sf = ScanFile(
            case_id=self.id,
            filename=pathlib.Path(filepath).name,
            created_at=datetime.now(timezone.utc),
        )  # UTC 시간 기록
        db.session.add(sf)
        self.updated_at = datetime.now(timezone.utc)  # 업데이트 시간 역시 UTC
        db.session.commit()
        
# ----------------------------
#  스캔 파일 ------------------
# ----------------------------
class ScanFile(db.Model):
    __tablename__ = 'scan_file'
    id         = db.Column(db.Integer, primary_key=True)        # ✅ PK!
    case_id    = db.Column(db.Integer, db.ForeignKey('case.id'), nullable=False)
    filename   = db.Column(db.String(256), nullable=False)
    created_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )  # UTC 기준으로 생성되는 timezone-aware 필드

    case = db.relationship('Case', backref='files')

    def to_dict(self):
        return {
            "id"        : self.id,
            "filename"  : self.filename,
            "created_at": self.created_at.isoformat(),
        }

# ----------------------------
#  XML 미수신 폴더 기록 ------
# ----------------------------
class PendingCase(db.Model):
    __tablename__ = 'pending_case'
    id = db.Column(db.Integer, primary_key=True)
    folder_name = db.Column(db.String(128), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

# -------------------------------------------------
#  DB 초기화 헬퍼 ----------------------------------
# -------------------------------------------------
def init_db(app):
    """Flask 앱 컨텍스트에서 테이블을 모두 생성한다."""
    with app.app_context():
        try:
            db.create_all()
        except Exception as e:
            # 이미 테이블이 존재하면 OperationalError 날 수 있으니 무시
            from sqlalchemy.exc import OperationalError
            if isinstance(e, OperationalError):
                app.logger.info("init_db: tables already exist, skipping create_all")
            else:
                raise

