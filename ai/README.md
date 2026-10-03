# Pose-ON AI

MediaPipe BlazePose 기반의 재활 운동 자세 분석 모듈입니다. 웹캠 자세를 기준 프로필과 비교해 동작 횟수, 자세 유사도, 피드백을 계산하고 스켈레톤 오버레이 영상을 저장합니다.

이 문서는 `ai/` 폴더의 실행 안내입니다. 프로젝트 루트의 README와 별도로 사용합니다.

## 현재 지원 범위

- 프론트엔드·백엔드 없이 로컬 웹캠 데모 실행
- 어깨 운동과 시선당기기 중 한 운동 선택
- 기준 영상 전처리를 통한 기준 프로필 JSON 생성
- 사용자 웹캠과 기준 영상 비교 화면, 로컬 한글 피드백 표시
- FastAPI WebSocket을 통한 JPEG 프레임 분석 및 결과 반환
- 로컬 스켈레톤 MP4 녹화
- 백엔드 점수·영상 경로 전송 클라이언트 준비

**백엔드 자동 전송과 전체 서비스 통합은 아직 완료되지 않았습니다.** FastAPI 서버를 켜는 것만으로 프론트엔드·백엔드 연결이나 웹캠 분석이 자동 시작되지는 않습니다.

## 1. 설치

기존 개발 환경은 Windows, Python 3.12.2입니다. 아래 명령은 Windows PowerShell 기준입니다. 프로젝트 루트에서 `ai` 폴더로 이동한 뒤 실행하세요.

```powershell
cd ai
py -3.12 -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

이미 가상환경이 있으면 생성 명령은 생략합니다. Python 3.12가 설치되어 있어야 `py -3.12` 명령을 사용할 수 있습니다.

실행 의존성과 테스트 의존성은 `requirements.txt` 하나로 관리합니다. `Pillow`는 한글 표시, `httpx`는 백엔드 통신, `pytest`는 테스트에 사용합니다.

가상환경 활성화가 제한된 경우에는 정책을 변경하지 않고 다음처럼 해당 Python을 직접 사용할 수 있습니다.

```powershell
.\venv\Scripts\python.exe -m pip install -r requirements.txt
```

이후의 `python` 명령도 같은 실행 파일로 바꿔 사용하면 됩니다. 이하 모든 명령의 작업 폴더는 `ai/`입니다.

## 2. 자세 추정 모델 준비

```powershell
python -m scripts.download_pose_model
```

기본 모델은 `lite`이며 `weights/pose_landmarker_lite.task`에 저장됩니다. 파일이 이미 있으면 다운로드를 건너뜁니다. 최초 다운로드에는 인터넷 연결이 필요합니다.

모델 변경 시에는 다운로드·전처리·실행에 동일한 설정을 사용하세요.

```powershell
$env:POSE_MODEL_VARIANT = "full"
python -m scripts.download_pose_model
```

## 3. 기준 영상과 프로필 준비

| 운동       | 운동 코드             | 기준 영상                                          | 기준 프로필                                        |
| ---------- | --------------------- | -------------------------------------------------- | -------------------------------------------------- |
| 어깨 운동  | `shoulder_open_close` | `storage/reference_videos/shoulder_open_close.mp4` | `storage/reference_cache/shoulder_open_close.json` |
| 시선당기기 | `gaze_pull`           | `storage/reference_videos/gaze_pull.mp4`           | `storage/reference_cache/gaze_pull.json`           |

기준 영상은 프로젝트 담당자가 공유한 원본을 위 파일명으로 배치합니다. 모델과 달리 기준 영상은 자동 다운로드하지 않습니다.

선택한 운동의 기준 프로필이 없거나 기준 영상·분석 구간을 바꿨다면 먼저 전처리합니다.

```powershell
python -m scripts.preprocess_reference --exercise shoulder_open_close
```

```powershell
python -m scripts.preprocess_reference --exercise gaze_pull
```

위 명령은 해당 운동의 JSON을 생성하거나 기존 파일을 덮어씁니다. 팀에서 공유한 프로필이 현재 영상·설정에 맞는다면 매번 다시 생성할 필요는 없습니다.

기본 분석 구간은 어깨 운동 10초부터 끝까지, 시선당기기 0~19초입니다. `core/exercise_catalog.py`에서 운동별 구간을 관리합니다. 시선당기기는 촬영 구도가 바뀌기 전 구간을 사용합니다.

필요하면 `--start-sec`와 `--end-sec`으로 구간을 지정할 수 있습니다. `--end-sec 0`은 영상 끝까지입니다. 구간을 변경했다면 전처리와 로컬 데모에 같은 구간을 지정하세요.

## 4. 로컬 웹캠 데모

두 명령 중 테스트할 운동 하나를 실행합니다.

```powershell
python -m scripts.run_local_demo --exercise shoulder_open_close
```

```powershell
python -m scripts.run_local_demo --exercise gaze_pull
```

- `--exercise`를 생략하면 어깨 운동이 선택됩니다.
- 선택한 운동의 기준 영상, 기준 프로필, 자세 추정 모델, 웹캠이 필요합니다.
- 화면 왼쪽은 사용자 웹캠, 오른쪽은 기준 영상입니다.
- 화면 창에 초점을 둔 상태에서 `q`를 누르면 종료합니다.
- 종료 시 반복 횟수, 평균 자세 유사도, 녹화 경로를 터미널에 출력합니다.

### 피드백과 녹화

한글 피드백은 로컬 표시용 화면에만 그립니다. 현재 자세를 매 프레임 재판정하여 해당 오류가 해소되면 문구를 지우고, 여러 오류가 있으면 우선순위에 따라 한 개를 표시합니다. 동작 단계가 바뀌면 평가하는 항목도 달라질 수 있습니다. 로그 출력 주기와 화면 표시 상태는 별도로 처리합니다.

녹화에는 사용자 스켈레톤 및 기본 분석 오버레이가 포함되며, 로컬 한글 피드백과 기준 영상 비교 패널은 포함되지 않습니다. 결과는 `storage/recordings/`에 저장됩니다. 무음·고정 FPS 녹화이므로 실제 프레임 처리 속도와 설정 FPS가 다르면 재생 시간이 실제 운동 시간과 다를 수 있습니다.

### 횟수와 점수의 의미

- 횟수는 운동별 동작 단계와 유지 조건을 충족했을 때 증가합니다.
- 시선당기기는 좌우 한 쌍이 아닌 한쪽 팔의 위→아래 완료를 1회로 셉니다.
- `accuracy`는 완료한 회차의 평균 기준 자세 유사도(0~100)입니다. 자세 추정 모델의 인식 정확도나 임상적 평가 지표가 아닙니다.
- `rep_scores`에는 완료한 각 회차의 점수가 저장됩니다.

## 5. FastAPI 서버 실행

```powershell
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

`--reload`는 개발용 옵션입니다. 서버 종료는 터미널에서 `Ctrl+C`입니다.

| 용도                      | 주소                                                                   |
| ------------------------- | ---------------------------------------------------------------------- |
| 상태 확인                 | `http://127.0.0.1:8000/health`                                         |
| HTTP API 문서             | `http://127.0.0.1:8000/docs`                                           |
| 어깨 운동 WebSocket 예시  | `ws://127.0.0.1:8000/ws/exercise/12?exercise_code=shoulder_open_close` |
| 시선당기기 WebSocket 예시 | `ws://127.0.0.1:8000/ws/exercise/12?exercise_code=gaze_pull`           |

예시의 `12`는 세션 ID입니다. 실제 백엔드 연동에서는 백엔드가 발급한 ID를 사용해야 합니다. 로컬 데모의 `local_...` ID를 백엔드에 그대로 보내면 안 됩니다.

WebSocket 클라이언트는 JPEG 이미지 바이트를 전송합니다. AI 서버는 준비 완료 JSON(`ready`), 분석 JSON(`analysis`), 오버레이 JPEG 바이트 등을 반환합니다. 운동 종료 명령은 텍스트 JSON `{"type":"stop"}`이며 요약(`summary`)을 받은 후 연결이 닫힙니다. 오류는 `error` 형식으로 전달됩니다. 일반 연결 해제 시에는 녹화를 닫고 자원을 정리하지만 종료 요약 전송은 보장하지 않습니다.

WebSocket 테스트는 별도 클라이언트가 필요합니다. `/docs`에서 JPEG 프레임 분석을 직접 실행하는 구조는 아닙니다. 웹 클라이언트의 Origin은 `FRONTEND_ORIGINS`와 일치해야 합니다.

## 6. 주요 설정

`core/config.py`는 프로세스 환경변수를 읽습니다. `.env` 파일을 만들기만 해서는 자동 적용되지 않습니다. 값을 바꾼 후 프로그램을 다시 실행하세요.

| 환경변수              | 기본값                  | 용도                                          |
| --------------------- | ----------------------- | --------------------------------------------- |
| `POSE_MODEL_VARIANT`  | `lite`                  | `lite`, `full`, `heavy` 모델 선택             |
| `CAMERA_INDEX`        | `0`                     | 로컬 데모 웹캠 번호                           |
| `LOCAL_FEEDBACK_FONT` | 자동 탐색               | 로컬 화면용 한글 폰트 파일 경로               |
| `FRONTEND_ORIGINS`    | `http://localhost:5173` | 허용할 프론트엔드 Origin, 여러 개면 쉼표 구분 |
| `RECORDING_FPS`       | `24`                    | 저장 영상의 고정 FPS                          |
| `VIDEO_CODEC`         | `mp4v`                  | 녹화 코덱                                     |
| `BACKEND_ENABLED`     | `False`                 | 백엔드 클라이언트 요청 활성화 여부            |
| `BACKEND_BASE_URL`    | `http://localhost:8080` | 백엔드 서버 주소                              |

예를 들어 웹캠 번호는 다음처럼 바꿉니다.

```powershell
$env:CAMERA_INDEX = "1"
python -m scripts.run_local_demo --exercise gaze_pull
```

한글 폰트를 찾지 못하면 실제 설치된 폰트 경로를 지정하세요.

```powershell
$env:LOCAL_FEEDBACK_FONT = "C:\Windows\Fonts\malgun.ttf"
```

## 7. 백엔드 연동 상태와 제한

`clients/backend_client.py`에는 다음 메서드가 준비되어 있습니다.

| 메서드                                    | 전달 내용                                                      |
| ----------------------------------------- | -------------------------------------------------------------- |
| `send_scores(session_id, rep_scores)`     | 회차별 점수를 `scores` 배열의 `actionNo`, `actionScore`로 변환 |
| `send_video_path(session_id, video_path)` | `{"videoPath": "경로 또는 URL"}` 전송; 파일 업로드 아님        |

현재 `exercise_ws.py`와 로컬 데모는 이 메서드들을 자동 호출하지 않습니다. `BACKEND_ENABLED=True`만 설정해도 자동 전송되는 것은 아닙니다.

백엔드와 협의하거나 연결해야 할 사항:

1. AI가 보내지 않는 `angleDiff`에 대해 백엔드 DTO의 필수 검증, Mapper와 DB 제약조건 수정
2. 영상 실제 저장·업로드 방식과 다른 서버 및 브라우저에서 접근할 방법
3. 백엔드 세션 ID 전달, 운동 코드 매핑, 점수 저장 성공 후 세션 종료 순서
4. 정수 점수 저장 여부, 중복 전송, 0회·중도 종료, 통신 실패 및 인증 정책
5. AI 종료 처리에 전송 호출을 연결한 뒤 통합 테스트

점수는 현재 백엔드 Integer 형식에 맞춰 `round()`로 정수화합니다. AI 화면의 소수점 점수 평균과 백엔드 정수 점수 평균은 차이가 날 수 있습니다. 현재 확인한 백엔드는 종료 시 저장된 점수로 횟수와 평균을 계산하므로 점수 저장 전에 종료하면 안 됩니다. 같은 전체 점수 목록을 반복 전송하면 중복 저장될 수 있어 자동 재시도는 하지 않습니다.

## 8. 테스트

```powershell
python -m pytest tests -q
```

테스트 통과는 웹캠 장치, 영상 재생·녹화 또는 백엔드 통합 동작까지 보장하지 않습니다. 로컬 데모와 실제 연동 테스트는 별도로 진행하세요.

## 9. 파일 위치 안내

| 위치                  | 역할                                        |
| --------------------- | ------------------------------------------- |
| `main.py`             | FastAPI 실행 진입점                         |
| `core/`               | 공통 설정, 운동 목록, CLI 옵션              |
| `models/`             | 특징·프로필·세션 상태·응답 모델             |
| `services/pose/`      | 자세 추정과 스켈레톤 표시                   |
| `services/exercises/` | 운동별 특징 추출, 횟수 판정, 자세 점수 계산 |
| `services/reference/` | 기준 영상 분석 및 프로필 저장·조회          |
| `services/feedback/`  | 피드백 문구와 우선순위                      |
| `services/session/`   | 세션 상태 및 녹화 관리                      |
| `services/recorder/`  | MP4 저장                                    |
| `routers/`            | 상태 API 및 WebSocket                       |
| `clients/`            | 백엔드 HTTP 클라이언트                      |
| `scripts/`            | 모델 다운로드, 기준 전처리, 로컬 데모       |
| `tests/`              | 자동 테스트                                 |

시선당기기 점수 가중치는 `services/exercises/gaze_pull.py`의 `SCORE_WEIGHTS`, 어깨 운동 점수 계산은 `services/exercises/shoulder_open_close.py`의 `_rep_score()`에서 확인할 수 있습니다. 점수 계산과 피드백·횟수 판정 임계값은 같은 개념이 아닙니다.

## 10. 자주 발생하는 문제와 Git 공유

- **모듈을 찾을 수 없음:** `ai/`에서 가상환경 Python으로 `python -m ...` 형식으로 실행했는지 확인합니다.
- **기준 프로필이 없음:** 선택한 운동의 영상 배치 후 전처리 명령을 실행합니다.
- **기준 영상을 열 수 없음:** 운동 코드와 MP4 파일명, 파일 경로 및 재생 가능 여부를 확인합니다.
- **웹캠을 열 수 없음:** 다른 앱의 카메라 점유, 카메라 권한, `CAMERA_INDEX`를 확인합니다.
- **한글 폰트 오류:** 한글 폰트를 설치하고 `LOCAL_FEEDBACK_FONT`를 지정합니다.
- **백엔드 점수 전송 거절:** `angleDiff` 필수 조건이 수정됐는지, 세션 ID가 백엔드에 실제 존재하는지 확인합니다.

가상환경, Python 캐시, 개인 녹화 영상, 비밀 설정값은 Git에 올리지 않습니다. 이 파일들을 로컬에서 삭제할 필요는 없습니다. `.gitignore`는 이미 추적 중인 파일을 자동으로 추적 해제하지 않으므로 커밋 대상도 확인하세요.
