package com.seniorrehab.model.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;

@Getter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class GuardianTokenResponseDto {

    private Long sessionId;   // 검증 성공 시, 어떤 운동 세션 결과인지 알려주는 용도
}