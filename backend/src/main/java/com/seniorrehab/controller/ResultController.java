package com.seniorrehab.controller;

import com.seniorrehab.model.dto.ExerciseRecordDto;
import com.seniorrehab.model.dto.ResultSaveRequestDto;
import com.seniorrehab.service.ResultService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
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

    // 운동 결과 단건 조회
    @GetMapping("/result/{resultId}")
    public ResponseEntity<?> getResult(
            @AuthenticationPrincipal String userId,
            @PathVariable Long resultId) {

        ExerciseRecordDto record = resultService.getResult(resultId);
        if (record == null) {
            return ResponseEntity.status(HttpStatus.NOT_FOUND)
                    .body(Map.of("error", "존재하지 않는 결과입니다"));
        }

        if (record.getUserId() == null || !record.getUserId().equals(Long.parseLong(userId))) {
            return ResponseEntity.status(HttpStatus.FORBIDDEN)
                    .body(Map.of("error", "본인의 운동 결과만 조회할 수 있습니다"));
        }

        return ResponseEntity.ok(record);
    }

    // 보호자 공유 링크로 운동 결과 조회 (비회원 접근 가능)
    @GetMapping("/result/share/{token}")
    public ResponseEntity<ExerciseRecordDto> getSharedResult(@PathVariable String token) {
        ExerciseRecordDto record = resultService.getSharedResult(token);
        return ResponseEntity.ok(record);
    }
}