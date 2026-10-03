package com.seniorrehab.model.dto;

import lombok.Getter;
import lombok.Setter;
import java.time.LocalTime;

@Getter
@Setter
public class ScheduleDto {
    private Long scheduleId;
    private String exerciseDay;
    private LocalTime exerciseTime;
    private Boolean useAlert;
    private Long userId;
    private String tel;
    private String name;
    private String guardianTel;
}