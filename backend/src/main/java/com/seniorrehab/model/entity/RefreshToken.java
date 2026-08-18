package com.seniorrehab.model.entity;

import java.time.LocalDateTime;

import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

@Getter
@Setter
@NoArgsConstructor
public class RefreshToken {
    
    private Long tokenId;
    private Long userId;
    private String token;
    private LocalDateTime expiredAt;
    private LocalDateTime createdAt;
}
