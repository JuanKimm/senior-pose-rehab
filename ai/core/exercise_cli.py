"""전처리/로컬 데모가 함께 사용하는 운동 선택 인자입니다."""

import argparse

from core.exercise_catalog import EXERCISES, get_exercise


def parse_exercise_args(description: str):
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--exercise", choices=list(EXERCISES), default="shoulder_open_close")
    parser.add_argument("--start-sec", type=float, default=None)
    parser.add_argument("--end-sec", type=float, default=None, help="0이면 영상 끝까지")
    args = parser.parse_args()
    spec = get_exercise(args.exercise)
    start = spec.start_sec if args.start_sec is None else args.start_sec
    end = spec.end_sec if args.end_sec is None else args.end_sec
    if start < 0 or end < 0 or (end and end <= start):
        parser.error("0 <= start < end여야 합니다. end=0은 영상 끝입니다.")
    return spec, start, end
