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
    int claimSession(@Param("sessionId") Long sessionId, @Param("userId") Long userId); // 게스트 세션을 로그인한 계정에 연결 (결과 저장)
    int updateVideoPath(@Param("sessionId") Long sessionId, @Param("videoPath") String videoPath); // 스켈레톤 오버레이 영상 경로 저장
}