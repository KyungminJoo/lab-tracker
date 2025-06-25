from flask import Blueprint, render_template

ui_bp = Blueprint("ui", __name__)

@ui_bp.route("/case/<int:case_id>", methods=["GET"])
def case_detail(case_id):
    """브라우저에서 /case/<id> 요청 시 HTML 템플릿 반환."""
    return render_template("case_detail.html", case_id=case_id)

@ui_bp.route("/cases")
def case_list_page():
    """브라우저에서 /cases 요청 시 HTML 목록 템플릿 반환."""
    return render_template("case_list.html")
