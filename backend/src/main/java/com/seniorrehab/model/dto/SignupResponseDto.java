package com.seniorrehab.model.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;

// 회원가입 성공 응답 - 민감정보(password, status) 제외
@Getter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class SignupResponseDto {

    private Long userId;   // DB의 회원 번호 (PK, 자동 증가)
    private String tel;    // 본인 전화번호
    private String name;   // 사용자 이름
}