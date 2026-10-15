package com.seniorrehab.model.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Pattern;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

@Getter
@Setter
@NoArgsConstructor
public class UpdateUserRequestDto {

    @NotBlank(message = "전화번호를 입력해주세요")
    @Pattern(regexp = "^010[0-9]{8}$", message = "전화번호는 11자리여야 합니다")
    private String tel;

    @NotBlank(message = "이름을 입력해주세요")
    private String name;

    @Pattern(regexp = "^(010[0-9]{8})?$", message = "보호자 연락처는 11자리여야 합니다")
    private String guardianTel;
}