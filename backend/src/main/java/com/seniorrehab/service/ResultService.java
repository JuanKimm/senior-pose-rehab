package com.seniorrehab.service;

import com.seniorrehab.model.dto.ExerciseRecordDto;
import com.seniorrehab.repository.SessionMapper;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

@Service
@RequiredArgsConstructor
public class ResultService {

    private final SessionMapper sessionMapper;

    // 운동 결과 저장 - 세션을 로그인한 사용자 계정에 연결
    public ExerciseRecordDto saveResult(Long userId, Long sessionId) {
        ExerciseRecordDto session = sessionMapper.findSessionById(sessionId);
        if (session == null) {
            return null;
        }
        if (session.getUserId() != null) {
            throw new IllegalArgumentException("이미 저장된 세션입니다");
        }

        sessionMapper.claimSession(sessionId, userId);
        return sessionMapper.findSessionById(sessionId);
    }
}