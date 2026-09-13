package com.seniorrehab.model.dto;

import jakarta.validation.constraints.NotNull;
import lombok.Getter;
import lombok.Setter;

// EXERCISE_SCORE 동작 1개에 대응하는 요청 데이터
@Getter
@Setter
public class ScoreItemDto {

    @NotNull(message = "동작 번호가 필요합니다")
    private Integer actionNo;

    @NotNull(message = "각도 차이값이 필요합니다")
    private Float angleDiff;

    @NotNull(message = "동작 점수가 필요합니다")
    private Integer actionScore;
}