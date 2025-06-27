from flask import current_app as app

from .models import db, Case


def print_label(case: Case) -> None:
    """라벨 프린터 스텁."""
    app.logger.info("▶ 라벨 프린트 (stub): %s", case.case_id)


def save_case_and_print_label(case_name: str, stl_path: str):
    """호환용 함수. 케이스 생성 후 파일을 추가하고 프린터 스텁 호출."""
    case = Case.query.filter_by(case_id=case_name).first()
    if case is None:
        case = Case(case_id=case_name, status="scan완료")
        db.session.add(case)
        db.session.commit()

    case.add_file(stl_path)
    print_label(case)
    return True
