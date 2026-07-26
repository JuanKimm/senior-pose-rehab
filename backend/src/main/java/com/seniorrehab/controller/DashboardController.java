package com.seniorrehab.controller;

import com.seniorrehab.model.dto.ExerciseRecordDto;
import com.seniorrehab.service.DashboardService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/dashboard")
@RequiredArgsConstructor
public class DashboardController {

    private final DashboardService dashboardService;

    // 오늘 운동 기록 조회
    @GetMapping("/today")
    public ResponseEntity<ExerciseRecordDto> getTodayRecord(
            @AuthenticationPrincipal String userId) {
        ExerciseRecordDto record = dashboardService.getTodayRecord(Long.parseLong(userId));
        return ResponseEntity.ok(record);
    }
}