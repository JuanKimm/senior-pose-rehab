package com.seniorrehab.model.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;

@Getter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class RefreshTokenResponseDto {

    private String accessToken;   // 새로 발급된 액세스 토큰
}