package com.seniorrehab.model.dto;

import jakarta.validation.constraints.NotBlank;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

// 회원 탈퇴 요청 시 받을 데이터
@Getter
@Setter
@NoArgsConstructor
public class WithdrawRequestDto {

    @NotBlank(message = "비밀번호를 입력해주세요")
    private String password;
}