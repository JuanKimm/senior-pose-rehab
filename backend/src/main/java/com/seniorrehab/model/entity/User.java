package com.seniorrehab.model.entity;

import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

import java.time.LocalDateTime;

@Getter
@Setter
@NoArgsConstructor
public class User {

    private Long userId;            // user_id
    private String tel;             // 로그인 아이디 (전화번호)
    private String password;        // BCrypt 암호화된 비밀번호
    private String name;            // 사용자 이름
    private String guardianTel;     // 보호자 연락처 (nullable)
    private String role;            // ROLE_USER 등
    private String status;          // ACTIVE / WITHDRAWN
    private LocalDateTime createdAt;
}