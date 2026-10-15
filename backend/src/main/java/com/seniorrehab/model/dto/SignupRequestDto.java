package com.seniorrehab.model.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Pattern;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

// 회원가입 요청 시 받을 데이터
@Getter
@Setter
@NoArgsConstructor
public class SignupRequestDto {

    @NotBlank(message = "전화번호를 입력해주세요")
    @Pattern(regexp = "^010[0-9]{8}$", message = "전화번호는 11자리여야 합니다")
    private String tel;

    @NotBlank(message = "비밀번호를 입력해주세요")
    @Pattern(regexp = "^[0-9]{6}$", message = "비밀번호는 숫자 6자리여야 합니다")
    private String password;

    @NotBlank(message = "이름을 입력해주세요")
    private String name;

    // 보호자 연락처는 선택 (빈 값 허용)
    @Pattern(regexp = "^(010[0-9]{8})?$", message = "보호자 연락처는 11자리여야 합니다")
    private String guardianTel;
}