package com.seniorrehab.model.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Pattern;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

// 비밀번호 변경 요청 시 받을 데이터
@Getter
@Setter
@NoArgsConstructor
public class ChangePasswordRequestDto {

    @NotBlank(message = "기존 비밀번호를 입력해주세요")
    private String currentPassword;

    @NotBlank(message = "새 비밀번호를 입력해주세요")
    @Pattern(regexp = "^[0-9]{6}$", message = "비밀번호는 숫자 6자리여야 합니다")
    private String newPassword;
}