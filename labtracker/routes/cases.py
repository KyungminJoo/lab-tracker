from flask import current_app
"""
Case-related API endpoints.

• PATCH /api/cases/bulk     – 다건 상태 변경
• GET   /api/cases          – 목록 조회
• GET   /api/cases/<id>     – 단건 조회
"""

from datetime import datetime
from flask import request, jsonify, send_from_directory

from . import bp
from ..models import Case, ScanFile, db

# 허용 상태값
VALID_STATUSES = {
    "스캔->디자인",
    "디자인->밀링",
    "밀링->신터링&글레이징",
    "기공완료",
}


# ─────────────────────────────────────────────────────────────
# bulk PATCH
# ─────────────────────────────────────────────────────────────
@bp.route("/api/cases/bulk", methods=["PATCH"])
def bulk_update():
    data = request.get_json() or {}
    ids = data.get("ids", [])
    new_status = data.get("new_status")

    if not ids or new_status not in VALID_STATUSES:
        return jsonify({"msg": "ids, new_status 필수"}), 400

    updated_rows = (
        Case.query.filter(Case.id.in_(ids))
        .update(
            {"status": new_status, "updated_at": datetime.utcnow()},
            synchronize_session=False,
        )
    )
    db.session.commit()
    return jsonify({"updated": updated_rows}), 200


# ─────────────────────────────────────────────────────────────
# 목록 GET
# ─────────────────────────────────────────────────────────────
@bp.route("/api/cases", methods=["GET"])   # ← /cases → /api/cases
def list_cases():
    rows = (
        Case.query.with_entities(Case.id, Case.status, Case.updated_at)
        .order_by(Case.id.asc())
        .all()
    )
    data = [
        {
            "id": r.id,
            "status": r.status,
            "updated_at": r.updated_at.isoformat() if r.updated_at else None,
        }
        for r in rows
    ]
    return jsonify(data), 200


# ─────────────────────────────────────────────────────────────
# 단건 GET
# ─────────────────────────────────────────────────────────────
@bp.route("/api/cases/<int:case_id>", methods=["GET"])
def get_case(case_id):
    row = Case.query.get_or_404(case_id)
    return jsonify(
        {
            "id": row.id,
            "status": row.status,
            "updated_at": row.updated_at.isoformat() if row.updated_at else None,
        }
    ), 200

# ─────────────────────────────────────────────────────────────
#  상태 PATCH /api/cases/<id>/status
# ─────────────────────────────────────────────────────────────
@bp.route("/api/cases/<int:case_id>/status", methods=["PATCH"])
def update_status(case_id: int):
    """단일 케이스의 상태를 변경한다."""
    payload = request.get_json() or {}
    new_status = payload.get("status")
    if new_status not in VALID_STATUSES:
        return jsonify({"msg": "invalid status"}), 400

    case = Case.query.get_or_404(case_id)
    case.status = new_status
    case.updated_at = datetime.utcnow()
    db.session.commit()
    return jsonify({"status": case.status}), 200

# ─────────────────────────────────────────────────────────────
#  단일 케이스의 파일 목록  GET /api/cases/<id>/files
# ─────────────────────────────────────────────────────────────
@bp.route("/api/cases/<int:case_id>/files")
def case_files(case_id):
    case = Case.query.get_or_404(case_id)
    return jsonify([f.to_dict() for f in case.files]), 200

# --- 라벨 재출력 (프린터 연결 전까지는 로그만) ---
@bp.route('/api/cases/<int:case_id>/print_label', methods=['POST'])
def print_label(case_id):
    Case.query.get_or_404(case_id)
    current_app.logger.info("▶ 라벨 프린트 요청: case %s", case_id)
    return {"ok": True}

# routes/cases.py 맨 아래에 붙이기
from pathlib import Path

@bp.route("/api/cases/<int:case_id>/files", methods=["POST"])
def upload_file(case_id):
    case = Case.query.get_or_404(case_id)

    f = request.files.get("file")
    if not f or f.filename == "":
        return jsonify({"msg": "no file"}), 400

    save_path = Path("/app/data/uploads")
    save_path.mkdir(parents=True, exist_ok=True)
    f.save(save_path / f.filename)

    sf = ScanFile(case_id=case.id, filename=f.filename)
    db.session.add(sf)
    db.session.commit()
    return jsonify(sf.to_dict()), 201


# ---------------------------------------------------------------------------
#  파일 다운로드
# ---------------------------------------------------------------------------
@bp.route('/api/files/<int:file_id>/download')
def download_file(file_id: int):
    """저장된 스캔 파일을 클라이언트로 전송한다."""
    sf = ScanFile.query.get_or_404(file_id)
    file_path = Path('/app/data/uploads') / sf.filename
    return send_from_directory(file_path.parent, file_path.name, as_attachment=True)
