package com.seniorrehab.model.dto;

import jakarta.validation.constraints.NotNull;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

@Getter
@Setter
@NoArgsConstructor
public class ResultSaveRequestDto {

    @NotNull(message = "세션 ID가 필요합니다")
    private Long sessionId;
}