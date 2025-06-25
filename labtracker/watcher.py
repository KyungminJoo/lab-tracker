from watchdog.events import FileSystemEventHandler

# ── inotify용 기본 Observer ──
from watchdog.observers import Observer

# ── PollingObserver: 버전에 따라 모듈 위치가 다르므로 try/except ──
try:
    from watchdog.observers.polling import PollingObserver   # ✔️  watchdog 4.x
except ImportError:
    # 아주 오래된 watchdog 0.x 에서는 polling 서브모듈이 없음
    PollingObserver = None

import os, pathlib, re, time, threading

CASE_REGEX = re.compile(r'^([^\s]+)\s+.*\.stl$', re.I)

# ── 1. 이벤트 핸들러 ────────────────────────────────────────────
class ScanHandler(FileSystemEventHandler):
    def __init__(self, app):
        self.app = app
        super().__init__()

    def on_created(self, event):
        if event.is_directory or not event.src_path.lower().endswith(".stl"):
            return

        # ── 1-A.  잠깐 기다려서 파일 쓰기 완료 보장 (0.5 초 x 6 회) ──
        for _ in range(6):
            prev = os.path.getsize(event.src_path)
            time.sleep(0.5)
            if os.path.getsize(event.src_path) == prev:
                break     # 사이즈가 더 안 변하면 탈출

        stem = pathlib.Path(event.src_path).stem
        m = CASE_REGEX.match(stem)
        if not m:
            self.app.logger.info(f"🚫  규칙 불일치 → {stem}")
            return

        case_name = m.group(1)
        self.app.logger.info(f"🆕  새 스캔: {case_name} ({event.src_path})")

        from .services import save_case_and_print_label
        with self.app.app_context():
            save_case_and_print_label(case_name, event.src_path)

# ── 2. 시작 함수 ───────────────────────────────────────────────
def start_watcher(app):
    watch_path = pathlib.Path(app.config["WATCH_PATH"])

    def _run():
        try:
            obs = Observer()               # inotify
            obs.schedule(ScanHandler(app), str(watch_path), recursive=False)
            obs.start()
            app.logger.info("✅ inotify Observer started")
        except Exception:
            obs = PollingObserver(timeout=1.0)    # Fallback
            obs.schedule(ScanHandler(app), str(watch_path), recursive=False)
            obs.start()
            app.logger.warning("⏱  Fallback to PollingObserver")

        obs.join()

    threading.Thread(target=_run, daemon=True).start()
