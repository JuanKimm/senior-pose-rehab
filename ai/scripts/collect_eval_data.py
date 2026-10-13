# 사용 방법
#   1. 시작 시 정상 동작(1) / 틀린 동작(2) 중 무엇을 10회 수집할지 입력
#   2. 창에서 s: 시작 -> 운동 1회 수행 -> e: 종료 (영상 + JSON 저장, 프로그램은 계속 실행)
#   3. 목표 횟수(기본 10)를 채우면 x 키 눌러 프로그램을 종료
#
# 실행 (ai 폴더에서)
#   python -m scripts.collect_eval_data --subject 본인이름
#
# 저장 위치
#   storage/recordings/eval/<운동코드>/normal/<피험자>_<운동코드>_normal_01.mp4 / .json
#   storage/recordings/eval/<운동코드>/wrong/<피험자>_<운동코드>_wrong_01.mp4 / .json
import argparse
import json
import os
import re
import shutil
from datetime import datetime

from pathlib import Path
from time import monotonic, perf_counter

import cv2
import numpy as np

from core.config import (
    CAMERA_INDEX,
    POSE_MODEL_PATH,
    POSE_MODEL_VARIANT,
    RECORDING_DIR,
    RECORDING_FPS,
    ensure_directories,
)
from core.exercise_catalog import EXERCISES, get_exercise
from services.feedback.feedback_engine import FEEDBACK_MESSAGES, FEEDBACK_PRIORITY
from services.pose.blazepose_estimator import BlazePoseEstimator
from services.pose.pose_renderer import draw_pose
from services.reference.reference_repository import ReferenceRepository
from services.session.session_manager import SessionManager

WINDOW_NAME = "Eval collect | s: start  e: end  x: exit"
LABELS = {
    "1": ("normal", "정상 동작"),
    "2": ("wrong", "틀린 동작"),
}
EXPECTED_REPS_PER_CLIP = 1

def _load_korean_font(size: int = 26):
    """한글 폰트를 찾지 못해도 오류 없이 None을 반환합니다(그 경우 영문으로 표시)."""
    try:
        from PIL import ImageFont
    except ImportError:
        return None
    custom = os.getenv("LOCAL_FEEDBACK_FONT")
    candidates = (
        [Path(custom)]
        if custom
        else [
            Path(os.getenv("WINDIR", "C:/Windows")) / "Fonts/malgun.ttf",
            Path("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"),
            Path("/usr/share/fonts/truetype/nanum/NanumGothic.ttf"),
            Path("/System/Library/Fonts/AppleSDGothicNeo.ttc"),
        ]
    )
    for path in candidates:
        try:
            if path.is_file():
                return ImageFont.truetype(str(path), size=size)
        except OSError:
            continue
    return None


def _draw_banner(frame, lines: list[str], font, color=(24, 37, 48)):
    """화면 하단에 안내 문구 박스를 그린 복사본을 반환합니다(녹화 프레임은 바꾸지 않음)."""
    lines = [line for line in lines if line]
    if not lines:
        return frame
    if font is None: 
        out = frame.copy()
        height = out.shape[0]
        for i, line in enumerate(reversed(lines)):
            text = line.encode("ascii", "ignore").decode() or "-"
            cv2.putText(out, text, (16, height - 16 - i * 30), cv2.FONT_HERSHEY_SIMPLEX,
                        0.8, (255, 255, 255), 2, cv2.LINE_AA)
        return out

    from PIL import Image, ImageDraw

    image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(image)
    margin, padding = 12, 14
    line_height = font.size + 8
    box_height = 2 * padding + len(lines) * line_height
    top = max(margin, image.height - margin - box_height)
    draw.rounded_rectangle((margin, top, image.width - margin, image.height - margin),
                           radius=12, fill=color)
    for i, line in enumerate(lines):
        draw.text((margin + padding, top + padding + i * line_height), line,
                  font=font, fill=(255, 255, 255), anchor="lt")
    return cv2.cvtColor(np.asarray(image), cv2.COLOR_RGB2BGR)


def _draw_big_number(frame, text: str):
    out = frame.copy()
    height, width = out.shape[:2]
    cv2.putText(out, text, (width // 2 - 40, height // 2 + 40), cv2.FONT_HERSHEY_SIMPLEX,
                4.0, (0, 255, 255), 8, cv2.LINE_AA)
    return out


def _display_feedback(session, features) -> tuple[str, str]:
    """run_local_demo와 동일하게 현재 자세를 매 프레임 재판정해 표시용 문구를 고릅니다."""
    if features is None:
        return "POSE_NOT_DETECTED", FEEDBACK_MESSAGES.get("POSE_NOT_DETECTED", "")
    try:
        codes = session.analyzer.current_feedback(features, session.profile, session.state)
    except Exception:  
        return "", ""
    code = next((item for item in FEEDBACK_PRIORITY if item in codes), "")
    return code, FEEDBACK_MESSAGES.get(code, "")


def _ask_label() -> tuple[str, str]:
    while True:
        answer = input(
            "수집할 동작을 선택하세요.\n"
            "  정상 동작 10회를 진행하시려면 1\n"
            "  틀린 동작 10회를 진행하시려면 2\n"
            "입력 > "
        ).strip()
        if answer in LABELS:
            return LABELS[answer]
        print("1 또는 2만 입력해 주세요.\n")


def _safe_name(value: str, fallback: str) -> str:
    cleaned = re.sub(r"[^\w-]", "_", value.strip(), flags=re.UNICODE).strip("_")
    return cleaned or fallback


def _ask_subject(preset: str | None) -> str:
    if preset is not None:
        return _safe_name(preset, "P01")
    answer = input("피험자 이름 또는 ID를 입력하세요 (그냥 Enter면 P01) > ")
    return _safe_name(answer, "P01")


def _existing_indices(out_dir: Path, prefix: str) -> list[int]:
    pattern = re.compile(rf"^{re.escape(prefix)}_(\d+)\.(?:mp4|json)$")
    found = set()
    if out_dir.is_dir():
        for path in out_dir.iterdir():
            match = pattern.match(path.name)
            if match:
                found.add(int(match.group(1)))
    return sorted(found)


def _write_json_atomic(path: Path, data: dict) -> None:
    tmp = path.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    tmp.replace(path)


def _landmarks_to_list(pose) -> list[list[float]]:
    return [
        [round(p.x, 4), round(p.y, 4), round(p.z, 4), round(p.visibility, 3)]
        for p in pose.normalized
    ]


def _latency_stats(values: list[float]) -> dict:
    if not values:
        return {"mean": None, "p95": None, "max": None}
    arr = np.asarray(values, dtype=float)
    return {
        "mean": round(float(arr.mean()), 2),
        "p95": round(float(np.percentile(arr, 95)), 2),
        "max": round(float(arr.max()), 2),
    }


class Trial:
    """s ~ e 사이의 세션 하나. 기존 SessionManager/분석기를 그대로 사용합니다."""

    def __init__(self, manager, profile, session_id, label_code, save_landmarks):
        self.manager = manager
        self.session_id = session_id
        self.label_code = label_code
        self.save_landmarks = save_landmarks
        self.session = manager.start(session_id, profile)
        self.started_wall = datetime.now()
        self.started_at = monotonic()
        self.frames: list[dict] = []
        self.rep_events: list[dict] = []
        self.feedback_events: list[dict] = []
        self.latencies: list[float] = []
        self.pose_frames = 0
        self.image_size: tuple[int, int] | None = None  # (width, height)
        self._last_feedback = ""
        self.closed = False

    def process(self, frame, estimator, timestamp_ms: int, exercise_code: str):
        """프레임 한 장을 run_local_demo와 같은 순서로 처리하고 화면용 프레임을 반환합니다."""
        session = self.session
        if self.image_size is None:
            self.image_size = (frame.shape[1], frame.shape[0])

        t0 = perf_counter()
        timestamp_ms = max(timestamp_ms, session.state.last_pose_timestamp_ms + 1)
        session.state.last_pose_timestamp_ms = timestamp_ms
        session.state.frame_count += 1

        pose = estimator.detect(frame, timestamp_ms)
        if pose is None:
            analysis = self.manager.pose_missing(self.session_id, timestamp_ms)
        else:
            analysis = self.manager.process_pose(self.session_id, pose, timestamp_ms)
            self.pose_frames += 1
        latency_ms = (perf_counter() - t0) * 1000.0
        self.latencies.append(latency_ms)

        rendered = draw_pose(
            frame,
            pose,
            session.state.phase,
            session.state.rep_count,
            session.state.accuracy,
            analysis.features,
            exercise_code=exercise_code,
        )
        self.manager.record(self.session_id, rendered)

        display_code, display_message = _display_feedback(session, analysis.features)
        elapsed_ms = int((monotonic() - self.started_at) * 1000)
        record = {
            "i": len(self.frames),
            "t_ms": elapsed_ms,
            "pose_detected": pose is not None,
            "phase": session.state.phase,
            "rep_count": session.state.rep_count,
            "latency_ms": round(latency_ms, 2),
            "features": analysis.features.model_dump(mode="json") if analysis.features else None,
            "feedback_code": analysis.feedback_code,
            "display_feedback_code": display_code,
        }
        if self.save_landmarks and pose is not None:
            record["landmarks"] = _landmarks_to_list(pose)
        self.frames.append(record)

        evaluation = analysis.evaluation
        if evaluation is not None and evaluation.rep_completed:
            self.rep_events.append(
                {"t_ms": elapsed_ms, "frame": record["i"], "rep_no": session.state.rep_count,
                 "rep_score": evaluation.rep_score}
            )
        if display_code and display_code != self._last_feedback:
            self.feedback_events.append({"t_ms": elapsed_ms, "frame": record["i"], "code": display_code})
        self._last_feedback = display_code
        return rendered, display_message

    def finish(self):
        """녹화를 닫고 (상태, 임시 영상 경로)를 반환합니다."""
        self.closed = True
        result = self.manager.end(self.session_id)
        if result is None:
            return self.session.state, None
        return result


def _build_result(trial: Trial, *, spec, subject, label_code, label_name, index, args,
                  video_name, duration_sec, profile) -> dict:
    state = trial.session.state
    frames = len(trial.frames)
    return {
        "meta": {
            "created_at": trial.started_wall.isoformat(timespec="seconds"),
            "subject": subject,
            "exercise_code": spec.code,
            "exercise_name": spec.name,
            "label": label_code,
            "label_name": label_name,
            "clip_index": index,
            "expected_rep_count": EXPECTED_REPS_PER_CLIP,
            "video_file": video_name,
            "camera_index": args.camera,
            "pose_model_variant": POSE_MODEL_VARIANT,
            "recording_fps": RECORDING_FPS,
            "image_width": trial.image_size[0] if trial.image_size else None,
            "image_height": trial.image_size[1] if trial.image_size else None,
            "landmarks_saved": bool(args.save_landmarks),
            "landmark_format": "per frame: 33 x [x, y, z, visibility] (normalized image coords)",
            "profile_thresholds": (
                profile.thresholds.model_dump(mode="json") if hasattr(profile, "thresholds") else None
            ),
        },
        "result": {
            "rep_count": state.rep_count,
            "rep_count_error": state.rep_count - EXPECTED_REPS_PER_CLIP,
            "rep_scores": list(state.rep_scores),
            "accuracy": state.accuracy,
            "left_rep_count": state.left_rep_count,
            "right_rep_count": state.right_rep_count,
            "final_phase": state.phase,
            "duration_sec": round(duration_sec, 2),
            "frame_count": frames,
            "pose_detected_frames": trial.pose_frames,
            "pose_missing_frames": frames - trial.pose_frames,
            "effective_fps": round(frames / duration_sec, 2) if duration_sec > 0 else None,
            "latency_ms": _latency_stats(trial.latencies),
        },
        "rep_events": trial.rep_events,
        "feedback_events": trial.feedback_events,
        "frames": trial.frames,
    }


def parse_args():
    parser = argparse.ArgumentParser(description="검증용 정상/틀린 동작 수집 (시작~종료 단위 저장)")
    parser.add_argument("--exercise", choices=list(EXERCISES), default="shoulder_open_close")
    parser.add_argument("--subject", default=None, help="피험자 이름/ID (생략하면 실행 시 입력)")
    parser.add_argument("--target", type=int, default=10, help="클래스별 수집 목표 개수(기본 10)")
    parser.add_argument("--camera", type=int, default=CAMERA_INDEX)
    parser.add_argument("--countdown", type=int, default=3, help="s를 누른 뒤 녹화 시작까지 초(0=즉시)")
    parser.add_argument("--no-landmarks", dest="save_landmarks", action="store_false",
                        help="프레임별 관절 좌표를 JSON에 저장하지 않음(용량 절감)")
    args = parser.parse_args()
    if args.target < 1 or args.countdown < 0:
        parser.error("--target은 1 이상, --countdown은 0 이상이어야 합니다.")
    return args


_window_seen = False


def _window_closed() -> bool:
    """창이 한 번 표시된 뒤 X 버튼으로 닫힌 경우에만 True (백엔드별 오탐 방지)."""
    global _window_seen
    try:
        visible = cv2.getWindowProperty(WINDOW_NAME, cv2.WND_PROP_VISIBLE)
    except cv2.error:
        return False
    if visible >= 1:
        _window_seen = True
        return False
    return _window_seen


def main() -> None:
    args = parse_args()
    spec = get_exercise(args.exercise)
    ensure_directories()

    label_code, label_name = _ask_label()
    subject = _ask_subject(args.subject)

    out_dir = RECORDING_DIR / "eval" / spec.code / label_code
    out_dir.mkdir(parents=True, exist_ok=True)
    prefix = f"{subject}_{spec.code}_{label_code}"
    existing = _existing_indices(out_dir, prefix)
    saved = len(existing)
    next_index = (existing[-1] + 1) if existing else 1
    print(f"\n운동: {spec.name} | 동작: {label_name} | 피험자: {subject}")
    print(f"저장 폴더: {out_dir}")
    if saved:
        print(f"이미 저장된 {saved}개를 이어서 진행합니다. (새 파일은 {next_index}번부터)")
    if saved >= args.target:
        print(f"이미 목표 {args.target}개를 채웠습니다. --target을 늘리거나 다른 피험자로 실행하세요.")
        return

    profile = ReferenceRepository(spec.profile_path).load()
    if profile.exercise_code != spec.code:
        raise ValueError("선택한 운동과 기준 프로필이 다릅니다.")
    font = _load_korean_font()
    estimator = BlazePoseEstimator(POSE_MODEL_PATH)
    capture = cv2.VideoCapture(args.camera)
    if not capture.isOpened():
        estimator.close()
        raise RuntimeError(f"웹캠 {args.camera}번을 열 수 없습니다.")

    manager = SessionManager()
    clock_started = monotonic()
    trial: Trial | None = None
    countdown_until: float | None = None
    notice = ""
    notice_until = 0.0

    def say(text: str, seconds: float = 4.0):
        nonlocal notice, notice_until
        notice, notice_until = text, monotonic() + seconds
        print(text)

    try:
        cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(WINDOW_NAME, 1100, 800)
        say("준비되면 s 키로 시작하세요. (영문 입력 상태에서 눌러주세요)", 6.0)
        while True:
            ok, frame = capture.read()
            if not ok:
                print("카메라 프레임을 읽을 수 없어 종료합니다.")
                break

            now = monotonic()
            status = f"[{label_name}] 저장 {saved}/{args.target}"
            lines: list[str] = []

            if trial is not None:
                timestamp_ms = int((now - clock_started) * 1000)
                shown, feedback_message = trial.process(frame, estimator, timestamp_ms, spec.code)
                lines = [f"● REC  {status} | 횟수 {trial.session.state.rep_count}  (끝나면 e)"
                         if font else f"REC {status} reps {trial.session.state.rep_count} (e: end)"]
                lines.append(feedback_message)
            elif countdown_until is not None:
                remain = countdown_until - now
                if remain <= 0:
                    countdown_until = None
                    session_id = f"eval_{subject}_{label_code}_{next_index:02d}"
                    trial = Trial(manager, profile, session_id, label_code, args.save_landmarks)
                    continue
                shown = _draw_big_number(frame, str(int(remain) + 1))
                lines = ["자세를 잡아주세요. 곧 녹화가 시작됩니다." if font else "Get ready..."]
            else:
                shown = frame
                if saved >= args.target:
                    lines = [f"{status}  목표 완료!", "x 키를 눌러 프로그램을 종료하세요." if font
                             else "Done. Press x to exit."]
                else:
                    lines = [f"{status}  다음은 {next_index}번째" if font else status,
                             "s: 시작   x: 종료" if font else "s: start  x: exit"]
                if notice and now < notice_until:
                    lines.append(notice)
            shown = _draw_banner(shown, lines, font)
            cv2.imshow(WINDOW_NAME, shown)

            key = cv2.waitKey(1) & 0xFF
            if _window_closed():
                key = ord("x")

            if key == ord("s") and trial is None and countdown_until is None and saved < args.target:
                if args.countdown > 0:
                    countdown_until = monotonic() + args.countdown
                else:
                    session_id = f"eval_{subject}_{label_code}_{next_index:02d}"
                    trial = Trial(manager, profile, session_id, label_code, args.save_landmarks)
            elif key == ord("e") and trial is not None:
                duration = monotonic() - trial.started_at
                active, trial = trial, None
                state, temp_video = active.finish()
                base = f"{prefix}_{next_index:02d}"
                video_path = out_dir / f"{base}.mp4"
                json_path = out_dir / f"{base}.json"
                try:
                    if temp_video is None:
                        raise RuntimeError("녹화된 프레임이 없습니다.")
                    shutil.move(str(temp_video), str(video_path))
                    result = _build_result(
                        active, spec=spec, subject=subject, label_code=label_code,
                        label_name=label_name, index=next_index, args=args,
                        video_name=video_path.name, duration_sec=duration, profile=profile,
                    )
                    _write_json_atomic(json_path, result)
                except Exception as exc:  
                    video_path.unlink(missing_ok=True)
                    say(f"저장 실패: {exc} (같은 번호로 다시 시도하세요)", 8.0)
                else:
                    saved += 1
                    next_index += 1
                    say(f"저장 완료: {base}  (횟수 {state.rep_count}, 점수 {state.accuracy})", 5.0)
                    if saved >= args.target:
                        say(f"{args.target}회 수집 완료! x 키로 프로그램을 종료하세요.", 30.0)
            elif key == ord("x"):
                if trial is not None:
                    say("녹화 중에는 종료할 수 없습니다. 먼저 e 키로 끝내 주세요.", 3.0)
                else:
                    break
    finally:
        if trial is not None and not trial.closed:
            _, leftover = trial.finish()
            if leftover is not None:
                Path(leftover).unlink(missing_ok=True)
            print("녹화 중이던 시도는 저장하지 않고 버렸습니다.")
        capture.release()
        cv2.destroyAllWindows()
        estimator.close()

    print(f"\n종료합니다. [{label_name}] 총 {saved}개 저장됨 -> {out_dir}")


if __name__ == "__main__":
    main()
