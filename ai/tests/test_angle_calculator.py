# 세 점 벡터로 계산한 관절 각도와 2차원 거리의 기본값을 검증합니다.
import pytest

from services.analysis.angle_calculator import angle_degrees, distance_2d


def test_right_angle() -> None:
    assert angle_degrees((1, 0, 0), (0, 0, 0), (0, 1, 0)) == pytest.approx(90.0)


def test_straight_angle() -> None:
    assert angle_degrees((-1, 0, 0), (0, 0, 0), (1, 0, 0)) == pytest.approx(180.0)


def test_distance_2d() -> None:
    assert distance_2d((0, 0), (3, 4)) == pytest.approx(5.0)


@pytest.mark.parametrize("invalid", [float("nan"), float("inf")])
def test_invalid_coordinate_is_rejected(invalid):
    with pytest.raises(ValueError):
        angle_degrees((invalid, 0, 0), (0, 0, 0), (0, 1, 0))
