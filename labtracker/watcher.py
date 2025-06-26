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

# 파일명에서 케이스 이름을 추출하기 위한 패턴 (확장자 무관)
CASE_REGEX = re.compile(r'^([^\s]+)\s+.*$', re.I)

# ── 1. 이벤트 핸들러 ────────────────────────────────────────────
class ScanHandler(FileSystemEventHandler):
    def __init__(self, app):
        self.app = app
        super().__init__()

    def on_created(self, event):
        # 디렉터리 생성은 무시하고 모든 파일을 감시한다
        if (
            event.is_directory
            or "/@eaDir/" in event.src_path
            or os.path.basename(event.src_path).startswith(".")
        ):            
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
            success = save_case_and_print_label(case_name, event.src_path)
            if not success:
                self.app.logger.warning("라벨 인쇄에 실패했습니다: lp 명령을 찾을 수 없습니다.")

# ── 2. 시작 함수 ───────────────────────────────────────────────
def start_watcher(app):
    if os.getenv("START_WATCHER", "1") != "1":
        app.logger.info("START_WATCHER=0 → 워처 비활성화")
        return

    watch_path = pathlib.Path(app.config["WATCH_PATH"])

    if not watch_path.exists():
        try:
            watch_path.mkdir(parents=True, exist_ok=True)
            app.logger.warning(f"📁  WATCH_PATH '{watch_path}' created")
        except Exception as e:
            app.logger.warning(
                f"🚫  WATCH_PATH '{watch_path}' not found and failed to create: {e}"
            )
            return

    def _run():
        try:
            obs = Observer()               # inotify
            obs.schedule(ScanHandler(app), str(watch_path), recursive=True)
            obs.start()
            app.logger.info("✅ inotify Observer started")
        except Exception as exc:
            if PollingObserver is None:
                app.logger.error("❌ PollingObserver 사용 불가 – 감시 기능 비활성화")
                app.logger.exception(exc)
                return
            try:
                obs = PollingObserver(timeout=1.0)    # Fallback
                obs.schedule(ScanHandler(app), str(watch_path), recursive=True)
                obs.start()
                app.logger.warning("⏱  Fallback to PollingObserver")
            except Exception:
                app.logger.exception("❌ PollingObserver 시작 실패")
                raise

        obs.join()

    threading.Thread(target=_run, daemon=True).start()
