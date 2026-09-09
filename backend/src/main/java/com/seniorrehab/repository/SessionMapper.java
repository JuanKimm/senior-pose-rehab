package com.seniorrehab.repository;

import com.seniorrehab.model.dto.ExerciseRecordDto;
import com.seniorrehab.model.entity.ExerciseSession;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

@Mapper
public interface SessionMapper {
    int insertSession(ExerciseSession session); // 운동 세션 시작
    int endSession(@Param("sessionId") Long sessionId); // 운동 세션 종료
    ExerciseRecordDto findSessionById(@Param("sessionId") Long sessionId); // 종료된 세션 결과 조회
}