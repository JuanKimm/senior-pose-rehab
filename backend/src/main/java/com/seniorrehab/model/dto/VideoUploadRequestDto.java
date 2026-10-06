package com.seniorrehab.model.dto;

import jakarta.validation.constraints.NotBlank;
import lombok.Getter;
import lombok.Setter;

@Getter
@Setter
public class VideoUploadRequestDto {

    @NotBlank(message = "영상 경로가 필요합니다")
    private String videoPath;
}