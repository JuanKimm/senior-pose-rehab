package com.seniorrehab.model.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;

// 로그인 성공 시 클라이언트에 보낼 데이터
@Getter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class LoginResponseDto {

    private String accessToken;   // JWT 토큰
    private Long userId;          // 로그인 아이디 (전화번호)
    private String name;          // 사용자 이름
    private String tel;           // 전화번호
    private String role;          // 사용자 역할
}