# 세 점의 벡터 내적으로 관절 각도를 계산하고 좌표 거리와 중점을 구합니다.
# 운동 종류와 무관하게 재사용할 수 있는 순수 수학 함수만 포함합니다.
from math import acos, degrees, hypot, isfinite, sqrt


def _xyz(point: object) -> tuple[float, float, float]:
    if hasattr(point, "x"):
        return float(point.x), float(point.y), float(point.z)
    values = list(point)  # type: ignore[arg-type]
    z = float(values[2]) if len(values) > 2 else 0.0
    return float(values[0]), float(values[1]), z


def angle_degrees(point_a: object, vertex_b: object, point_c: object) -> float:
    ax, ay, az = _xyz(point_a)
    bx, by, bz = _xyz(vertex_b)
    cx, cy, cz = _xyz(point_c)

    if not all(isfinite(value) for value in (ax, ay, az, bx, by, bz, cx, cy, cz)):
        raise ValueError("관절 좌표에 NaN 또는 무한대가 포함되어 있습니다.")

    vector_ba = (ax - bx, ay - by, az - bz)
    vector_bc = (cx - bx, cy - by, cz - bz)
    norm_ba = sqrt(sum(value * value for value in vector_ba))
    norm_bc = sqrt(sum(value * value for value in vector_bc))
    if norm_ba < 1e-8 or norm_bc < 1e-8:
        raise ValueError("각도를 계산할 세 점이 서로 충분히 떨어져 있지 않습니다.")

    cosine = sum(a * c for a, c in zip(vector_ba, vector_bc)) / (norm_ba * norm_bc)
    cosine = max(-1.0, min(1.0, cosine))
    return degrees(acos(cosine))


def distance_2d(point_a: object, point_b: object) -> float:
    ax, ay, _ = _xyz(point_a)
    bx, by, _ = _xyz(point_b)
    return hypot(ax - bx, ay - by)


def midpoint(point_a: object, point_b: object) -> tuple[float, float, float]:
    ax, ay, az = _xyz(point_a)
    bx, by, bz = _xyz(point_b)
    return (ax + bx) / 2.0, (ay + by) / 2.0, (az + bz) / 2.0
