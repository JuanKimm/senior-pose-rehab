package com.seniorrehab.model.dto;

import lombok.Getter;
import lombok.Setter;

@Getter
@Setter
public class BodyPartStatsDto {
    private String bodyPart;
    private Integer totalCount;
    private Float avgAccuracy;
}