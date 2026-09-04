package com.seniorrehab.repository;

import com.seniorrehab.model.dto.ExerciseTypeDto;
import org.apache.ibatis.annotations.Mapper;
import java.util.List;

@Mapper
public interface ExerciseMapper {
    List<ExerciseTypeDto> findExerciseTypes(); // 운동 카테고리 목록 조회
}