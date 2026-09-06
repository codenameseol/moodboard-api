# moodboard-api

## 오늘의 기분 한 줄 · One line for today's mood

텍스트 하나와 mood tag 하나를 SQLite에 저장하고 꺼내는 작은 FastAPI 연습입니다.
A small FastAPI exercise that stores and retrieves one line of text plus a mood tag in SQLite.

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white) ![FastAPI](https://img.shields.io/badge/FastAPI-005571?logo=fastapi&logoColor=white)

## API 표면 · API surface

| Method | Path | 설명 · Description |
| --- | --- | --- |
| `POST` | `/notes` | 노트 생성 / Create a note: `{"text":"...","mood":"..."}` |
| `GET` | `/notes` | 최신순 목록·mood filter / List newest first; filter with `?mood=calm` |
| `GET` | `/notes/{id}` | 단건 조회, 없으면 `404` / Read one; `404` when missing |
| `DELETE` | `/notes/{id}` | 단건 삭제, 없으면 `404` / Delete one; `404` when missing |

데이터는 표준 라이브러리 `sqlite3`로 로컬 `moodboard.db`에 저장합니다.
Data is stored in a local `moodboard.db` through the standard-library `sqlite3` module.

## 실행 · Run

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
curl -X POST http://127.0.0.1:8000/notes \
  -H "Content-Type: application/json" \
  -d '{"text":"오늘은 커피가 맛있었다","mood":"calm"}'
curl "http://127.0.0.1:8000/notes?mood=calm"
```

## 테스트 · Test

```bash
pip install -r requirements-dev.txt
pytest
```

테스트는 임시 SQLite 파일을 사용해 실제 DB를 건드리지 않습니다.
Tests use a temporary SQLite file and do not touch the real database.

## 한계 · Boundaries

인증·update endpoint·운영용 persistence는 아직 없습니다. 학습/데모용이며 production API라고 주장하지 않습니다.
Authentication, update endpoints, and production persistence are not included. This is a learning/demo API, not a production service.

## License

MIT
