package com.seniorrehab.model.dto;

import lombok.Getter;
import lombok.Setter;

@Getter
@Setter
public class MonthlySummaryDto {
    private Integer totalDays;           // 총 운동 일수
    private String mostFrequentPart;     // 가장 많이 운동한 부위
    private Float avgAccuracy;           // 평균 정확도
    private Integer avgDurationSec;      // 평균 운동 시간(초)
    private Float accuracyImprovement;   // 전월 대비 정확도 향상
}