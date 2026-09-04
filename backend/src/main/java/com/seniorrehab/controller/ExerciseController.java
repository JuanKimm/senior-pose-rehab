package com.seniorrehab.controller;

import com.seniorrehab.model.dto.ExerciseTypeDto;
import com.seniorrehab.service.ExerciseService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import java.util.List;

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
}