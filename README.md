# moodboard-api

오늘의 기분 한 줄을 기록하는 아주 작은 API

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?logo=fastapi&logoColor=white)

## 취향 노트

거창한 다이어리 앱을 만들고 싶었던 건 아니고, 그냥 하루에 한 줄, 지금 기분이 어떤지 적어두는 습관이 있으면 좋겠다는 생각에서 시작했습니다. 텍스트 하나, 기분 태그 하나 - 그게 전부예요. 작더라도, 실제로 매일 써볼 수 있는 걸 만들어보고 싶었습니다.

백엔드도, 프론트엔드도, 그 사이 어딘가에 있는 것들도 조금씩 다 만져보면서 배우고 있는 중이라, 이 프로젝트는 그중 "저장하고 꺼내오는" 가장 기본적인 부분을 SQLite와 FastAPI로 직접 만들어본 연습입니다. 완성된 정답보다 작은 시도와 발견을 나누고 싶어요.

## 무엇을 하나요

기분 노트 하나를 기준으로 만들기(create) / 읽기(read) / 지우기(delete)만 할 수 있는, 정말 작은 API입니다.

| Method | Path | 설명 |
| --- | --- | --- |
| `POST` | `/notes` | 노트 하나 만들기. `{"text": "...", "mood": "..."}` 를 보내면 `id`와 서버가 찍은 UTC 시각이 붙어서 돌아옵니다. |
| `GET` | `/notes` | 노트 전체를 최신순으로 목록 조회. `?mood=calm` 처럼 기분 태그로 필터링할 수 있습니다. |
| `GET` | `/notes/{id}` | 노트 하나 조회. 없으면 404. |
| `DELETE` | `/notes/{id}` | 노트 하나 삭제. 없으면 404. |

데이터는 표준 라이브러리 `sqlite3`로 로컬 `moodboard.db` 파일에 저장됩니다. DB 관련 코드는 전부 `app/storage.py` 한 곳에 모아 두어서, 나머지 코드는 SQL을 몰라도 읽을 수 있게 해두었습니다.

```
app/
  main.py      # FastAPI 앱과 라우트
  models.py    # pydantic 모델 (요청/응답 형태)
  storage.py   # sqlite3 접근 코드 (이 파일만 DB를 알고 있어요)
tests/
  test_api.py  # pytest + TestClient
```

## 써보기

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

노트 하나 남겨보기:

```bash
curl -X POST http://127.0.0.1:8000/notes \
  -H "Content-Type: application/json" \
  -d '{"text": "오늘은 커피가 유독 맛있었다", "mood": "calm"}'
```

`calm` 기분만 다시 꺼내보기:

```bash
curl "http://127.0.0.1:8000/notes?mood=calm"
```

## 테스트

```bash
pip install -r requirements-dev.txt
pytest
```

테스트는 매번 임시 sqlite 파일을 새로 만들어서 사용하기 때문에, 실행할 때마다 실제 `moodboard.db`를 건드리지 않습니다. `.github/workflows/test.yml`에 push/PR마다 pytest를 돌리는 아주 작은 워크플로우도 하나 넣어두었어요.

## 아직 부족한 것들

- 인증이 없습니다 (혼자 쓰는 용도라 아직은 괜찮다고 생각하고 있어요)
- 기분 태그가 자유 형식이라 오타가 나도 그냥 저장됩니다
- 노트 수정(update) 기능은 아직 없습니다

아직 배워가는 중입니다. 다음엔 이 위에 아주 작은 화면 하나 정도 올려볼까 생각 중이에요.

## License

MIT
