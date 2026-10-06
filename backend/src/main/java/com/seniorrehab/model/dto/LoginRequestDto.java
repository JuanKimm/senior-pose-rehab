package com.seniorrehab.model.dto;

import jakarta.validation.constraints.NotBlank;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

// 로그인 요청 시 받을 데이터
@Getter
@Setter
@NoArgsConstructor
public class LoginRequestDto {

    @NotBlank(message = "전화번호를 입력해주세요")
    private String tel;

    @NotBlank(message = "비밀번호를 입력해주세요")
    private String password;
}