# Pose-ON

시니어 라이프케어를 위한 영상 기반 AI 자세 분석 재활 서비스입니다.

본 프로젝트는 웹캠 기반 운동 영상을 활용하여 사용자의 재활 운동 자세를 분석하고, 운동 기록과 분석 결과를 대시보드에서 확인할 수 있도록 하는 캡스톤 디자인 프로젝트입니다.

## 프로젝트 개요

고령층의 재활 운동은 꾸준한 수행과 올바른 자세 유지가 중요합니다.  
본 서비스는 웹캠을 통해 사용자의 운동 영상을 수집하고, AI 자세 분석을 통해 관절 좌표, 관절 각도, 반복 횟수, 자세 피드백 등의 정보를 제공합니다.

사용자는 운동 후 대시보드에서 운동 기록, 월간 요약, 그래프 데이터, 저장된 운동 영상을 확인할 수 있습니다.

## 주요 기능

- 웹캠 기반 운동 영상 녹화
- 운동 영상 로컬 저장
- 저장된 영상 재생 및 다운로드
- AI 기반 자세 분석
- 관절 좌표 및 관절 각도 계산
- 운동 반복 횟수 측정
- 자세 오류 피드백 제공
- 운동 결과 저장
- 대시보드 기반 운동 기록 조회
- 운동 일정 관리
- 회원가입, 로그인, JWT 기반 인증

## 기술 스택

### Frontend

- React
- JavaScript
- Axios
- CSS

### Backend

- Java
- Spring Boot
- Spring Security
- JWT
- JPA
- MySQL

### AI

- Python
- FastAPI
- MediaPipe
- OpenCV

### Collaboration

- Git
- GitHub

## 서버 포트 번호

| 구분      | 주소                    | 설명             |
| --------- | ----------------------- | ---------------- |
| Frontend  | `http://localhost:5173` | React 개발 서버  |
| Backend   | `http://localhost:8080` | Spring Boot 서버 |
| AI Server | `http://localhost:8000` | FastAPI 서버     |
