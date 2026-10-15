package com.seniorrehab.model.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Pattern;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

@Getter
@Setter
@NoArgsConstructor
public class SmsVerifyRequestDto {

    @NotBlank(message = "전화번호를 입력해주세요")
    @Pattern(regexp = "^010[0-9]{8}$", message = "전화번호는 11자리여야 합니다")
    private String tel;

    @NotBlank(message = "인증번호를 입력해주세요")
    @Pattern(regexp = "^[0-9]{6}$", message = "인증번호는 6자리 숫자여야 합니다")
    private String code;
}