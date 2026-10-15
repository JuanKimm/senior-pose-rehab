package com.seniorrehab.service;

import com.seniorrehab.model.dto.ExerciseRecordDto;
import com.seniorrehab.model.dto.ShareTokenInfoDto;
import com.seniorrehab.repository.GuardianTokenMapper;
import com.seniorrehab.repository.SessionMapper;
import lombok.RequiredArgsConstructor;

import java.time.LocalDateTime;

import org.springframework.stereotype.Service;

@Service
@RequiredArgsConstructor
public class ResultService {

    private final SessionMapper sessionMapper;
    private final GuardianTokenMapper guardianTokenMapper;

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

    // 운동 결과 단건 조회
    public ExerciseRecordDto getResult(Long resultId) {
        return sessionMapper.findSessionById(resultId);
    }

    // 보호자 공유 링크로 운동 결과 조회 (토큰 검증 + 결과 반환)
    public ExerciseRecordDto getSharedResult(String token) {
        ShareTokenInfoDto info = guardianTokenMapper.findByShareToken(token);

        if (info == null) {
            throw new IllegalArgumentException("유효하지 않은 링크입니다.");
        }
        if (info.getTokenExpiresAt().isBefore(LocalDateTime.now())) {
            throw new IllegalArgumentException("만료되었거나 이미 사용된 링크입니다.");
        }

        return sessionMapper.findSessionById(info.getSessionId());
    }
}