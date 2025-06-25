# lab-tracker

스캔 폴더를 감시하여 케이스를 생성하고 라벨을 출력하는 Flask 애플리케이션입니다.

## 필요 조건

- **Python 3.11** 환경 또는 **Docker** 사용
- CUPS 라이브러리(`libcups2-dev`)가 필요하며, Docker 이미지는 자동으로 설치합니다.

## 로컬 실행 방법

1. 의존성 설치
   ```bash
   pip install -r requirements.txt
   ```
2. 서버 실행
   ```bash
   python -m labtracker.wsgi
   ```

## Docker 사용 방법

Docker가 설치되어 있다면 다음 명령으로 컨테이너를 빌드하고 실행할 수 있습니다.

```bash
docker compose up --build
```

환경 변수(스캔 폴더 위치, 프린터 이름 등)는 `docker-compose.yml`에서 수정할 수 있습니다.

## DB 초기화 및 마이그레이션

DB 파일은 `data/labtracker.db`에 생성됩니다. 스키마가 변경된 경우 기존 파일을 삭제하거나 아래 스크립트를 실행해 갱신할 수 있습니다.

```bash
# 새로 생성
rm -f data/labtracker.db
python -m labtracker.wsgi  # 최초 실행 시 테이블 자동 생성

# 또는 마이그레이션 스크립트 사용
python scripts/migrate_unique_case_name.py
```

## 주요 엔드포인트

- `GET /api/cases` – 케이스 목록 조회
- `GET /api/cases/<id>` – 단일 케이스 조회
- `PATCH /api/cases/bulk` – 여러 케이스의 상태 일괄 변경
- `GET /api/cases/<id>/files` – 케이스에 속한 파일 목록
- `POST /api/cases/<id>/files` – 파일 업로드
- `POST /api/cases/<id>/print_label` – 라벨 재출력
- UI 페이지: `/cases`, `/case/<id>`

## 워처 작동 방식

애플리케이션이 실행되면 `create_app()` 내부에서 `start_watcher()`가 호출되어
스캔 폴더 감시가 시작됩니다. 감시 대상 폴더는 환경 변수 `WATCH_PATH`로 지정하며
기본값은 프로젝트 루트 기준 `SCAN/`입니다. 폴더가 존재하지 않으면 시작 시 자동으로
생성됩니다.

워처는 `watchdog` 라이브러리의 `Observer`(inotify)를 우선 사용하고, 실패할 경우
`PollingObserver`로 대체됩니다. 따라서 Linux에서는 실시간 이벤트를 이용하고, 기타
환경에서는 1초 간격으로 폴링하여 변경 사항을 감지합니다.

폴더 안에 새 파일이 생기면 다음 순서로 케이스가 만들어집니다.

1. 파일 크기가 더 이상 변하지 않을 때까지 잠시 대기하여 쓰기 완료를 확인합니다.
2. 파일 이름의 첫 공백 앞 부분을 케이스 이름으로 사용합니다.
   - 예: `ABC123 상악.stl` → `ABC123`
3. 해당 이름의 케이스가 없으면 새 케이스를 만들고 상태를 **스캔→디자인**으로 설정합니다.
4. 파일 기록을 추가한 뒤 `lp` 명령을 사용해 라벨을 인쇄합니다.

프로젝트 최상위 폴더 구조는 다음과 같습니다.

```text
lab-tracker/
├── labtracker/           # 애플리케이션 코드
├── SCAN/                 # 감시 대상 폴더
├── data/                 # DB 및 업로드 파일 저장 위치
└── ...
```

위와 같이 SCAN 폴더에 파일이 추가되면 워처가 자동으로 케이스를 생성하고
라벨을 출력하게 됩니다.

