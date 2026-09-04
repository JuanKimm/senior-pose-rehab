package com.seniorrehab.service;

import com.seniorrehab.model.dto.ExerciseTypeDto;
import com.seniorrehab.model.dto.ExerciseVideoDto;
import com.seniorrehab.repository.ExerciseMapper;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import java.util.List;

@Service
@RequiredArgsConstructor
public class ExerciseService {

    private final ExerciseMapper exerciseMapper;

    // 운동 카테고리 목록 조회
    public List<ExerciseTypeDto> getExerciseTypes() {
        return exerciseMapper.findExerciseTypes();
    }

    // 카테고리별 기준 운동 영상 목록 조회
    public List<ExerciseVideoDto> getVideosByTypeId(Long typeId) {
        return exerciseMapper.findVideosByTypeId(typeId);
    }
}