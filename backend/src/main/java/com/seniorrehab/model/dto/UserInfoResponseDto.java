package com.seniorrehab.model.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;

@Getter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class UserInfoResponseDto {

    private String name;
    private String tel;
    private String guardianTel;
}