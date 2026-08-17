package com.seniorrehab.repository;

import java.time.LocalDate;
import java.util.List;

import com.seniorrehab.model.dto.AccuracyGraphDto;
import com.seniorrehab.model.dto.BodyPartStatsDto;
import com.seniorrehab.model.dto.ExerciseRecordDto;
import com.seniorrehab.model.dto.MonthlySummaryDto;

import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

@Mapper
public interface DashboardMapper {
    ExerciseRecordDto findTodayRecord(Long userId); // 오늘 운동 기록 조회
    List<ExerciseRecordDto> findRecentRecords(Long userId); // 최근 7일 운동 기록 조회
    List<ExerciseRecordDto> findAllRecords(Long userId); // 전체 운동 기록 조회
    List<ExerciseRecordDto> findRecordsByDate(@Param("userId") Long userId, @Param("date") String date); // 특정 날짜 운동 기록 조회
    ExerciseRecordDto findRecordById(@Param("userId") Long userId, @Param("sessionId") Long sessionId); // 운동 기록 단건 상세 조회
    MonthlySummaryDto findMonthlySummary(@Param("userId") Long userId, @Param("year") int year, @Param("month") int month); // 월간 요약 조회
    List<AccuracyGraphDto> findAccuracyGraph(@Param("userId") Long userId); // 날짜별 정확도 그래프 조회
    List<BodyPartStatsDto> findBodyPartStats(@Param("userId") Long userId, @Param("year") int year, @Param("month") int month); // 부위별 통계 조회
   
    // 피드백용 데이터 조회
    LocalDate findLastExerciseDate(Long userId); // 마지막 운동 날짜
    Integer findMonthlyExerciseDays(@Param("userId") Long userId, @Param("year") int year, @Param("month") int month); // 이번 달 운동 일수
    Integer findConsecutiveDays(Long userId); // 연속 운동 일수
    List<String> findMonthlyBodyParts(@Param("userId") Long userId, @Param("year") int year, @Param("month") int month); // 이번 달 운동한 부위 목록
}