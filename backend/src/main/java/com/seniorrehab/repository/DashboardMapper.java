package com.seniorrehab.repository;

import java.util.List;

import com.seniorrehab.model.dto.ExerciseRecordDto;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

@Mapper
public interface DashboardMapper {
    ExerciseRecordDto findTodayRecord(Long userId); // 오늘 운동 기록 조회
    List<ExerciseRecordDto> findRecentRecords(Long userId); // 최근 7일 운동 기록 조회
    List<ExerciseRecordDto> findAllRecords(Long userId); // 전체 운동 기록 조회
    List<ExerciseRecordDto> findRecordsByDate(@Param("userId") Long userId, @Param("date") String date); // 특정 날짜 운동 기록 조회
    ExerciseRecordDto findRecordById(@Param("userId") Long userId, @Param("sessionId") Long sessionId); // 운동 기록 단건 상세 조회
}