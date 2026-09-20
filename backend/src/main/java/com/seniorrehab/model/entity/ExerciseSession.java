package com.seniorrehab.model.entity;

import lombok.Getter;
import lombok.Setter;
import java.time.LocalDate;
import java.time.LocalDateTime;

@Getter
@Setter
public class ExerciseSession {
    private Long sessionId;
    private Long userId;
    private Long exerciseTypeId;
    private LocalDate exerciseDate;
    private Integer totalCount;
    private Integer durationSec;
    private Float accuracy;
    private String videoPath;
    private LocalDateTime createdAt;
}