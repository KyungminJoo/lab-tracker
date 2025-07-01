from flask import current_app as app

from .models import db, Case

import os
import subprocess
import tempfile
from PIL import Image, ImageDraw, ImageFont
import qrcode


def print_label(case: Case) -> None:
    """케이스 정보를 라벨 프린터로 전송한다."""
    printer = app.config.get("PRINTER_NAME") or os.getenv("PRINTER_NAME")
    if not printer:
        app.logger.info("PRINTER_NAME 미지정 – 인쇄 생략")
        return

    app.logger.info("▶ 라벨 프린트 시작: %s", case.case_id)

    site_url = app.config.get("SITE_URL", "")
    qr_data = f"{site_url}/cases/{case.id}"

    qr_img = qrcode.make(qr_data).resize((150, 150))
    img = Image.new("RGB", (400, 180), "white")
    img.paste(qr_img, (10, 15))
    draw = ImageDraw.Draw(img)
    font = ImageFont.load_default()

    y = 20
    draw.text((170, y), f"Case: {case.case_id}", font=font, fill="black")
    y += 40
    if case.patient_name:
        draw.text((170, y), case.patient_name, font=font, fill="black")
        y += 40
    draw.text((170, y), case.status_label, font=font, fill="black")

    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
        img.save(tmp.name, format="PNG")
        temp_path = tmp.name

    try:
        subprocess.run(["lp", "-d", printer, temp_path], check=True)
    except Exception as e:  # pragma: no cover - 환경에 따라 실패 가능
        app.logger.error("Print failed: %s", e)
    finally:
        try:
            os.remove(temp_path)
        except Exception:
            pass


def save_case_and_print_label(case_name: str, stl_path: str):
    """케이스를 저장한 뒤 라벨을 인쇄한다."""
    case = Case.query.filter_by(case_id=case_name).first()
    if case is None:
        case = Case(case_id=case_name, status="scan완료")
        db.session.add(case)
        db.session.commit()

    case.add_file(stl_path)
    print_label(case)
    return True
