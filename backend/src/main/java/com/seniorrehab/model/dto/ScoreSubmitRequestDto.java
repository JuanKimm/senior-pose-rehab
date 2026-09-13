package com.seniorrehab.model.dto;

import jakarta.validation.Valid;
import jakarta.validation.constraints.NotEmpty;
import lombok.Getter;
import lombok.Setter;

import java.util.List;

// API 요청 body
@Getter
@Setter
public class ScoreSubmitRequestDto {

    @NotEmpty(message = "점수 데이터가 필요합니다")
    @Valid
    private List<ScoreItemDto> scores;
}