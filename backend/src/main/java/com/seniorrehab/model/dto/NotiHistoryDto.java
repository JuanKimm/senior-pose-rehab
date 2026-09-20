package com.seniorrehab.model.dto;

import lombok.Getter;
import lombok.Setter;
import java.time.LocalDateTime;

@Getter
@Setter
public class NotiHistoryDto {
    private Long notificationId;
    private String notiType;
    private String status;
    private String targetTel;
    private LocalDateTime sentAt;
    private String shareToken;
    private LocalDateTime tokenExpiresAt;
}