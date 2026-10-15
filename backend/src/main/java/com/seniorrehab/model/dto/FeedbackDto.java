package com.seniorrehab.model.dto;

import lombok.Getter;
import lombok.Setter;

@Getter
@Setter
public class FeedbackDto {
    private String message;
    private String type; // FREQUENCY, ACCURACY, BODY_PART
}