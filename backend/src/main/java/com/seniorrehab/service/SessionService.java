package com.seniorrehab.service;

import com.seniorrehab.model.dto.SessionStartRequestDto;
import com.seniorrehab.model.dto.SessionStartResponseDto;
import com.seniorrehab.model.entity.ExerciseSession;
import com.seniorrehab.repository.ExerciseMapper;
import com.seniorrehab.repository.SessionMapper;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

@Service
@RequiredArgsConstructor
public class SessionService {

    private final SessionMapper sessionMapper;
    private final ExerciseMapper exerciseMapper;

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
}