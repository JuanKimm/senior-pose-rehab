package com.seniorrehab.repository;

import com.seniorrehab.model.dto.ScoreItemDto;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

import java.util.List;

@Mapper
public interface ScoreMapper {

    // 세션의 기존 점수 삭제 (같은 결과가 다시 전송돼도 중복 저장되지 않도록)
    int deleteScoresBySessionId(@Param("sessionId") Long sessionId);

    // 운동 점수 데이터 일괄 저장
    int insertScores(@Param("sessionId") Long sessionId, @Param("scores") List<ScoreItemDto> scores);
}