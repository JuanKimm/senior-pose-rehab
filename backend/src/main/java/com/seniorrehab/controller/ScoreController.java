package com.seniorrehab.controller;

import com.seniorrehab.model.dto.ScoreSubmitRequestDto;
import com.seniorrehab.service.ScoreService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequestMapping("/api/exercise")
@RequiredArgsConstructor
public class ScoreController {

    private final ScoreService scoreService;

    // 운동 점수 데이터 일괄 전송 (AI 서버 전용)
    @PostMapping("/session/{sessionId}/score")
    public ResponseEntity<?> submitScores(
            @PathVariable Long sessionId,
            @Valid @RequestBody ScoreSubmitRequestDto request) {

        boolean success = scoreService.submitScores(sessionId, request.getScores());
        if (!success) {
            return ResponseEntity.status(HttpStatus.NOT_FOUND)
                    .body(Map.of("error", "존재하지 않는 세션입니다"));
        }
        return ResponseEntity.ok().build();
    }
}