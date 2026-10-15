package com.seniorrehab.model.dto;

import jakarta.validation.constraints.NotNull;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

@Getter
@Setter
@NoArgsConstructor
public class SessionStartRequestDto {

    @NotNull(message = "운동 카테고리를 선택해주세요")
    private Long exerciseTypeId;
}