package com.seniorrehab.model.dto;

import lombok.Getter;
import lombok.Setter;
import java.time.LocalDate;

@Getter
@Setter
public class AccuracyGraphDto {
    private LocalDate exerciseDate;
    private Float avgAccuracy;
}