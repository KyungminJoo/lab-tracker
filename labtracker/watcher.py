import os
import time
from pathlib import Path
from typing import Optional

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
try:
    from watchdog.observers.polling import PollingObserver  # type: ignore
except Exception:  # pragma: no cover
    PollingObserver = None

from apscheduler.schedulers.background import BackgroundScheduler

from .models import db, Case, PendingCase
from .services import print_label
from utils.parser import parse_case_xml


def wait_for_xml(folder: Path, retries: int = 3, interval: int = 10) -> Optional[Path]:
    for _ in range(retries):
        candidates = [p for p in folder.glob("*.xml") if p.name != "Materials.xml"]
        if candidates:
            return candidates[0]
        time.sleep(interval)
    return None


def handle_case_folder(app, folder: Path) -> None:
    xml = wait_for_xml(folder)
    if xml is None:
        app.logger.warning("XML missing in %s", folder)
        with app.app_context():
            try:
                db.session.add(PendingCase(folder_name=folder.name))
                db.session.commit()
            except Exception as e:  # pragma: no cover
                app.logger.error("Failed to record pending case %s: %s", folder, e)
        return
    try:
        data = parse_case_xml(xml, folder)
        with app.app_context():
            if Case.query.filter_by(case_id=data["case_id"]).first():
                return
            case = Case(**data)
            db.session.add(case)
            db.session.commit()
            print_label(case)
            app.logger.info("INSERT %s", data["case_id"])
    except Exception:  # pragma: no cover
        app.logger.exception("Error handling folder %s", folder)


def rescan_all(app) -> None:
    base = Path(app.config["WATCH_PATH"])
    if not base.exists():
        return
    for folder in base.iterdir():
        if folder.is_dir():
            xml = wait_for_xml(folder, retries=1, interval=0)
            if not xml:
                continue
            try:
                data = parse_case_xml(xml, folder)
                with app.app_context():
                    if not Case.query.filter_by(case_id=data["case_id"]).first():
                        case = Case(**data)
                        db.session.add(case)
                        db.session.commit()
                        print_label(case)
            except Exception:  # pragma: no cover
                app.logger.exception("Rescan error in %s", folder)


class FolderHandler(FileSystemEventHandler):
    def __init__(self, app):
        self.app = app
        super().__init__()

    def on_created(self, event):
        if event.is_directory:
            handle_case_folder(self.app, Path(event.src_path))


def start_watcher(app):
    if os.getenv("START_WATCHER", "1") != "1":
        app.logger.info("START_WATCHER=0 → 워처 비활성화")
        return

    watch_path = Path(app.config["WATCH_PATH"])
    if not watch_path.exists():
        try:
            watch_path.mkdir(parents=True, exist_ok=True)
            app.logger.warning("📁  WATCH_PATH '%s' created", watch_path)
        except Exception as e:  # pragma: no cover
            app.logger.warning("🚫  WATCH_PATH '%s' not found: %s", watch_path, e)
            return

    def _run():
        try:
            obs = Observer()
            obs.schedule(FolderHandler(app), str(watch_path), recursive=True)
            obs.start()
            app.logger.info("✅ inotify Observer started")
        except Exception:
            if not PollingObserver:
                app.logger.error("❌ PollingObserver 사용 불가 – 감시 비활성화")
                return
            obs = PollingObserver(timeout=1.0)
            obs.schedule(FolderHandler(app), str(watch_path), recursive=True)
            obs.start()
            app.logger.warning("⏱  Fallback to PollingObserver")
        scheduler = BackgroundScheduler()
        scheduler.add_job(lambda: rescan_all(app), "interval", minutes=5)
        scheduler.start()
        obs.join()

    import threading

    threading.Thread(target=_run, daemon=True).start()
