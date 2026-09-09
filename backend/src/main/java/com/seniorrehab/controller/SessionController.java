package com.seniorrehab.controller;

import com.seniorrehab.model.dto.ExerciseRecordDto;
import com.seniorrehab.model.dto.SessionStartRequestDto;
import com.seniorrehab.model.dto.SessionStartResponseDto;
import com.seniorrehab.service.SessionService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import java.util.Map;

@RestController
@RequestMapping("/api/exercise")
@RequiredArgsConstructor
public class SessionController {

    private final SessionService sessionService;

    // 운동 세션 시작 - 비회원도 가능
    @PostMapping("/session/start")
    public ResponseEntity<SessionStartResponseDto> startSession(
            @AuthenticationPrincipal String userId,
            @Valid @RequestBody SessionStartRequestDto request) {

        Long parsedUserId = null;
        try {
            parsedUserId = Long.parseLong(userId);
        } catch (NumberFormatException ignored) {
            // 토큰 없이(비회원으로) 호출된 경우
        }

        SessionStartResponseDto response = sessionService.startSession(parsedUserId, request);
        return ResponseEntity.ok(response);
    }

    // 운동 세션 종료
    @PutMapping("/session/{sessionId}/end")
    public ResponseEntity<?> endSession(@PathVariable Long sessionId) {
        ExerciseRecordDto record = sessionService.endSession(sessionId);
        if (record == null) {
            return ResponseEntity.status(HttpStatus.NOT_FOUND)
                    .body(Map.of("error", "존재하지 않는 세션입니다"));
        }
        return ResponseEntity.ok(record);
    }
}