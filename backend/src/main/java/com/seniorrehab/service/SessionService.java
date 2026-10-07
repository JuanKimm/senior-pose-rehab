package com.seniorrehab.service;

import com.seniorrehab.model.dto.ExerciseRecordDto;
import com.seniorrehab.model.dto.SessionEndRequestDto;
import com.seniorrehab.model.dto.SessionStartRequestDto;
import com.seniorrehab.model.dto.SessionStartResponseDto;
import com.seniorrehab.model.entity.ExerciseSession;
import com.seniorrehab.repository.ExerciseMapper;
import com.seniorrehab.repository.ScoreMapper;
import com.seniorrehab.repository.SessionMapper;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@RequiredArgsConstructor
public class SessionService {

    private final SessionMapper sessionMapper;
    private final ExerciseMapper exerciseMapper;
    private final ScoreMapper scoreMapper;

    // 운동 세션 시작 - userId는 비회원이면 null
    public SessionStartResponseDto startSession(Long userId, SessionStartRequestDto request) {
        if (exerciseMapper.findExerciseTypeById(request.getExerciseTypeId()) == null) {
            throw new IllegalArgumentException("존재하지 않는 운동 카테고리입니다");
        }

        ExerciseSession session = new ExerciseSession();
        session.setUserId(userId);
        session.setExerciseTypeId(request.getExerciseTypeId());

        sessionMapper.insertSession(session);

        return SessionStartResponseDto.builder()
                .sessionId(session.getSessionId())
                .build();
    }

    // 운동 세션 종료 - AI가 보낸 결과를 한 번에 저장, 존재하지 않는 세션이면 null 반환
    // 1. 회차별 점수 저장 / 2. 횟수, 운동 시간 저장 / 3. 점수 평균으로 정확도 계산
    @Transactional
    public ExerciseRecordDto endSession(Long sessionId, SessionEndRequestDto request) {
        if (sessionMapper.findSessionById(sessionId) == null) {
            return null;
        }

        // 1. 점수 저장 (재전송 시 중복 저장되지 않도록 기존 점수 삭제 후 저장)
        scoreMapper.deleteScoresBySessionId(sessionId);
        if (!request.getScores().isEmpty()) {
            scoreMapper.insertScores(sessionId, request.getScores());
        }

        // 2, 3. 횟수/운동 시간 저장 + 정확도 평균 계산 (점수가 없으면 정확도는 NULL)
        sessionMapper.endSession(sessionId, request.getTotalCount(), request.getDurationSec());

        return sessionMapper.findSessionById(sessionId);
    }
}