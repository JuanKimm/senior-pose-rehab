package com.seniorrehab.model.dto;

import lombok.Getter;
import lombok.Setter;
import java.time.LocalDate;

@Getter
@Setter
public class ExerciseRecordDto {
    private Long sessionId;
    private String bodyPart;
    private Integer totalCount;
    private Integer durationSec;
    private Float accuracy;
    private String videoPath;
    private LocalDate exerciseDate;
}