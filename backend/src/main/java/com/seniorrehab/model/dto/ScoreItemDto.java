package com.seniorrehab.model.dto;

import jakarta.validation.constraints.Max;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotNull;
import lombok.Getter;
import lombok.Setter;

// EXERCISE_SCORE 동작 1개에 대응하는 요청 데이터 (angleDiff 제외)
@Getter
@Setter
public class ScoreItemDto {

    @NotNull(message = "동작 번호가 필요합니다")
    private Integer actionNo;

    @NotNull(message = "동작 점수가 필요합니다")
    @Min(value = 0, message = "동작 점수는 0 이상이어야 합니다")
    @Max(value = 100, message = "동작 점수는 100 이하여야 합니다")
    private Integer actionScore;
}