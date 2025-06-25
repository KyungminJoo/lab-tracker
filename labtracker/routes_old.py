from flask import Blueprint, jsonify, request, abort
from .models import db, Case

bp = Blueprint("api", __name__)

@bp.get("/cases")
def list_cases():
    cases = Case.query.order_by(Case.created_at.desc()).all()
    return jsonify([
        {
            "id": c.id,
            "name": c.name,
            "status": c.status,
            "files": [f.path for f in c.files],
            "created_at": c.created_at.isoformat(),
        }
        for c in cases
    ])

@bp.patch("/cases/<int:case_id>")
def change_status(case_id: int):
    case = Case.query.get_or_404(case_id)
    case.status = request.json.get("status", case.status)
    db.session.commit()
    return jsonify({"result": "ok", "status": case.status})

@bp.patch("/cases/bulk")
def bulk_change():
    payload = request.json or {}
    ids = payload.get("ids", [])
    status = payload.get("status")
    if not ids or status is None:
        abort(400, "ids, status 필수")
    cases = Case.query.filter(Case.id.in_(ids)).all()
    for c in cases:
        c.status = status
    db.session.commit()
    return jsonify({"updated": len(cases)})
