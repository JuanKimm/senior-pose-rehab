package com.seniorrehab.model.dto;

import lombok.Getter;
import lombok.Setter;

import java.time.LocalDateTime;

@Getter
@Setter
public class ShareTokenInfoDto {

    private Long sessionId;
    private LocalDateTime tokenExpiresAt;
}