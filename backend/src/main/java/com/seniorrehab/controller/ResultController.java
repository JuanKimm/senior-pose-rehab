package com.seniorrehab.controller;

import com.seniorrehab.model.dto.ExerciseRecordDto;
import com.seniorrehab.model.dto.ResultSaveRequestDto;
import com.seniorrehab.service.ResultService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import java.util.Map;

@RestController
@RequestMapping("/api/exercise")
@RequiredArgsConstructor
public class ResultController {

    private final ResultService resultService;

    // 운동 결과 저장 - 비회원은 저장 불가 (로그인 필요)
    @PostMapping("/result")
    public ResponseEntity<?> saveResult(
            @AuthenticationPrincipal String userId,
            @Valid @RequestBody ResultSaveRequestDto request) {

        ExerciseRecordDto record = resultService.saveResult(Long.parseLong(userId), request.getSessionId());
        if (record == null) {
            return ResponseEntity.status(HttpStatus.NOT_FOUND)
                    .body(Map.of("error", "존재하지 않는 세션입니다"));
        }
        return ResponseEntity.ok(record);
    }
}