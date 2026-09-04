package com.seniorrehab.repository;

import com.seniorrehab.model.dto.ExerciseTypeDto;
import com.seniorrehab.model.dto.ExerciseVideoDto;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;
import java.util.List;

@Mapper
public interface ExerciseMapper {
    List<ExerciseTypeDto> findExerciseTypes(); // 운동 카테고리 목록 조회
    List<ExerciseVideoDto> findVideosByTypeId(@Param("typeId") Long typeId); // 카테고리별 기준 운동 영상 목록 조회
    ExerciseVideoDto findVideoById(@Param("videoId") Long videoId); // 기준 운동 영상 단건 조회
}