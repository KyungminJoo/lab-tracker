import subprocess, tempfile
import os
import qrcode
from .models import db, Case
from flask import current_app as app

def save_case_and_print_label(case_name: str, stl_path: str):
    case = Case.query.filter_by(name=case_name).first()
    if case is None:
        case = Case(name=case_name, status="스캔->디자인")
        db.session.add(case)
        db.session.commit()   # ➜ case.id 확보

    # ② 파일 추가 → models.py 의 add_file 메서드 호출
    case.add_file(stl_path)
    qr_data = f"{app.config['SITE_URL']}/case/{case.id}"
    tmp = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
    qrcode.make(qr_data).save(tmp.name)

    printed = True
    try:
        subprocess.run(
            ["lp", "-d", app.config["PRINTER_NAME"], "-o", "fit-to-page", tmp.name],
            check=False,
        )
    except FileNotFoundError:
        printed = False
        app.logger.warning("'lp' 명령을 찾을 수 없습니다. 라벨이 인쇄되지 않았습니다.")

    try:
        os.remove(tmp.name)
    except OSError:
        app.logger.warning("Could not remove temporary QR code file: %s", tmp.name)

    return printed
