package com.seniorrehab.service;

import com.seniorrehab.model.dto.ScoreItemDto;
import com.seniorrehab.repository.ScoreMapper;
import com.seniorrehab.repository.SessionMapper;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.List;


@Service
@RequiredArgsConstructor
public class ScoreService {

    private final ScoreMapper scoreMapper;
    private final SessionMapper sessionMapper;

    // AI 연동 - 운동 점수 데이터 일괄 저장
    public boolean submitScores(Long sessionId, List<ScoreItemDto> scores) {
        if (sessionMapper.findSessionById(sessionId) == null) {
            return false;
        }
        scoreMapper.insertScores(sessionId, scores);
        return true;
    }
}