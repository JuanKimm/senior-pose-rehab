package com.seniorrehab.model.dto;

import jakarta.validation.Valid;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotNull;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

import java.util.List;

// 운동 세션 종료 요청 - AI 서버가 운동 종료 시 결과를 한 번에 전송
@Getter
@Setter
@NoArgsConstructor
public class SessionEndRequestDto {

    @NotNull(message = "운동 횟수가 필요합니다")
    @Min(value = 0, message = "운동 횟수는 0 이상이어야 합니다")
    private Integer totalCount;     // AI summary.rep_count

    @NotNull(message = "운동 시간이 필요합니다")
    @Min(value = 0, message = "운동 시간은 0 이상이어야 합니다")
    private Integer durationSec;    // AI summary.duration_sec

    // 회차별 점수 목록 (0회 운동이면 빈 목록)
    @NotNull(message = "점수 데이터가 필요합니다")
    @Valid
    private List<ScoreItemDto> scores;
}