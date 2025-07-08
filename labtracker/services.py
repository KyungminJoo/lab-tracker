from datetime import datetime
from flask import current_app as app
from .models import db, Case
import os, subprocess, tempfile
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import qrcode


# ────────────────────────────── 라벨 프린터 전송 ──────────────────────────────
def print_label(case: Case) -> None:
    printer = app.config.get("PRINTER_NAME") or os.getenv("PRINTER_NAME")
    output_dir = app.config.get("LABEL_OUTPUT_DIR") or os.getenv("LABEL_OUTPUT_DIR")

    app.logger.info("▶ 라벨 프린트 시작: %s", case.case_id)

    site_url = app.config.get("SITE_URL", "")
    qr_img = qrcode.make(f"{site_url}/cases/{case.id}").resize((150, 150))

    img = Image.new("RGB", (400, 180), "white")
    img.paste(qr_img, (10, 15))
    draw, font, y = ImageDraw.Draw(img), ImageFont.load_default(), 20
    draw.text((170, y), f"Case: {case.case_id}", font=font, fill="black")
    y += 40
    if case.patient_name:
        draw.text((170, y), case.patient_name, font=font, fill="black")
        y += 40
    draw.text((170, y), case.status_label, font=font, fill="black")

    if output_dir:
        path = Path(output_dir)
        path.mkdir(parents=True, exist_ok=True)
        out_file = path / f"{case.case_id}.png"
        img.save(out_file, format="PNG")
        app.logger.info("라벨 이미지를 %s 에 저장했습니다", out_file)
        return

    if not printer:
        app.logger.info("PRINTER_NAME 미지정 – 인쇄 생략")
        return

    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
        img.save(tmp.name, format="PNG")
        temp_path = tmp.name

    try:
        subprocess.run(["lp", "-d", printer, temp_path], check=True)
    except Exception as e:  # 병원 밖에서 테스트 중이면 항상 실패할 수 있음
        app.logger.error("Print failed: %s", e)
    finally:
        try:
            os.remove(temp_path)
        except Exception:
            pass


# ────────────────────────────── “있으면 갱신·없으면 생성” ──────────────────────────────
def save_case_and_print_label(case_name: str, stl_path: str) -> bool:
    """
    1. case_id(case_name) 로 DB 에서 먼저 찾는다.
    2. 없으면 새로 만들고, 있으면 status·시간만 갱신한다.
    3. STL 파일을 케이스에 추가한 뒤 라벨 인쇄.
    """
    # 1) SELECT
    case: Case | None = Case.query.get(case_name)

    if case is None:
        # ─ 신규 폴더일 때 ───────────────────────────────────────
        case = Case(case_id=case_name,
                    status="scan완료",
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow())
        db.session.add(case)
    else:
        # ─ 이미 있던 폴더일 때 → 상태·업데이트시간만 갱신 ───────
        case.status      = "scan완료"
        case.updated_at  = datetime.utcnow()

    db.session.commit()           # INSERT 또는 UPDATE 확정

    # 2) STL 파일 경로 저장 (내부에서 다시 커밋됨)
    case.add_file(stl_path)

    # 3) 라벨 프린트(프린터 미연결 시 로그만 남김)
    print_label(case)
    return True