package com.seniorrehab.model.dto;

import lombok.Getter;
import lombok.Setter;

@Getter
@Setter
public class ExerciseTypeDto {
    private Long exerciseTypeId;
    private String bodyPart;
    private String description;
    private String hashtags;
    private String cardImagePath;
}