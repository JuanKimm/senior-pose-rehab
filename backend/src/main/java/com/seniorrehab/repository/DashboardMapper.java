package com.seniorrehab.repository;

import com.seniorrehab.model.dto.ExerciseRecordDto;
import org.apache.ibatis.annotations.Mapper;

@Mapper
public interface DashboardMapper {
    ExerciseRecordDto findTodayRecord(Long userId); // 오늘 운동 기록 조회
}