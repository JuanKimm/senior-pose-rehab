package com.seniorrehab.model.dto;

import lombok.Getter;
import lombok.Setter;

@Getter
@Setter
public class ExerciseVideoDto {
    private Long videoId;
    private Long exerciseTypeId;
    private String bodyPart;
    private String title;
    private String videoPath;
}