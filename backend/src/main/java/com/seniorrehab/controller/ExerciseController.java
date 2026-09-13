package com.seniorrehab.controller;

import com.seniorrehab.model.dto.ExerciseTypeDto;
import com.seniorrehab.model.dto.ExerciseVideoDto;
import com.seniorrehab.service.ExerciseService;
import lombok.RequiredArgsConstructor;

import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/exercise")
@RequiredArgsConstructor
public class ExerciseController {

    private final ExerciseService exerciseService;

    // 운동 카테고리 목록 조회
    @GetMapping("/types")
    public ResponseEntity<List<ExerciseTypeDto>> getExerciseTypes() {
        List<ExerciseTypeDto> types = exerciseService.getExerciseTypes();
        return ResponseEntity.ok(types);
    }

    // 카테고리별 기준 운동 영상 목록 조회
    @GetMapping("/{typeId}/videos")
    public ResponseEntity<List<ExerciseVideoDto>> getVideosByTypeId(@PathVariable Long typeId) {
        List<ExerciseVideoDto> videos = exerciseService.getVideosByTypeId(typeId);
        return ResponseEntity.ok(videos);
    }

    // 기준 운동 영상 단건 조회
    @GetMapping("/video/{videoId}")
    public ResponseEntity<?> getVideoById(@PathVariable Long videoId) {
        ExerciseVideoDto video = exerciseService.getVideoById(videoId);
        if (video == null) {
            return ResponseEntity.status(HttpStatus.NOT_FOUND)
                    .body(Map.of("error", "해당하는 영상이 없습니다."));
        }
        return ResponseEntity.ok(video);
    }
}