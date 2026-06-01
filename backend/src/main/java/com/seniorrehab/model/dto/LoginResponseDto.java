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
    private Long userId;          // DB의 회원 번호 (PK, 자동 증가)
    private String name;          // 사용자 이름
    private String tel;           // 본인 전화번호 (로그인 아이디로도 사용)
    private String role;          // 권한 (ROLE_USER 등)
}