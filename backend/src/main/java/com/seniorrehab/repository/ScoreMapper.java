package com.seniorrehab.repository;

import com.seniorrehab.model.dto.ScoreItemDto;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

import java.util.List;

@Mapper
public interface ScoreMapper {

    // AI 연동 - 운동 점수 데이터 일괄 저장
    int insertScores(@Param("sessionId") Long sessionId, @Param("scores") List<ScoreItemDto> scores);
}