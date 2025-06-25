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

## 주요 엔드포인트

- `GET /api/cases` – 케이스 목록 조회
- `GET /api/cases/<id>` – 단일 케이스 조회
- `PATCH /api/cases/bulk` – 여러 케이스의 상태 일괄 변경
- `GET /api/cases/<id>/files` – 케이스에 속한 파일 목록
- `POST /api/cases/<id>/files` – 파일 업로드
- `POST /api/cases/<id>/print_label` – 라벨 재출력
- UI 페이지: `/cases`, `/case/<id>`

## 워처 작동 방식

`WATCH_PATH`(기본값 `/app/SCAN`) 경로와 그 하위 폴더를 실시간으로 감시하여 새 파일이 생기면 확장자에 상관없이 케이스 이름을 추출해 DB에 저장하고 라벨을 프린터로 전송합니다. 이 과정은 백그라운드 스레드에서 실행됩니다. 경로가 존재하지 않으면 애플리케이션이 실행될 때 자동으로 생성되며, 생성에 실패하면 경고 로그가 출력됩니다.
