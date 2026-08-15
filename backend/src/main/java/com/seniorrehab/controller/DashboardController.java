package com.seniorrehab.controller;

import com.seniorrehab.model.dto.ExerciseRecordDto;
import com.seniorrehab.service.DashboardService;
import lombok.RequiredArgsConstructor;

import java.util.List;

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

    // 최근 7일 운동 기록 조회
    @GetMapping("/recent-records")
    public ResponseEntity<List<ExerciseRecordDto>> getRecentRecords(
            @AuthenticationPrincipal String userId) {
        List<ExerciseRecordDto> records = dashboardService.getRecentRecords(Long.parseLong(userId));
        return ResponseEntity.ok(records);
    }

    // 전체 운동 기록 조회
    @GetMapping("/recent-records/all")
    public ResponseEntity<List<ExerciseRecordDto>> getAllRecords(
            @AuthenticationPrincipal String userId) {
        List<ExerciseRecordDto> records = dashboardService.getAllRecords(Long.parseLong(userId));
        return ResponseEntity.ok(records);
    }

    // 특정 날짜 운동 기록 조회
    @GetMapping("/recent-records/{date}")
    public ResponseEntity<List<ExerciseRecordDto>> getRecordsByDate(
            @AuthenticationPrincipal String userId,
            @PathVariable String date) {
        List<ExerciseRecordDto> records = dashboardService.getRecordsByDate(Long.parseLong(userId), date);
        return ResponseEntity.ok(records);
    }

    // 운동 기록 단건 상세 조회
    @GetMapping("/records/{recordId}")
    public ResponseEntity<ExerciseRecordDto> getRecordById(
            @AuthenticationPrincipal String userId,
            @PathVariable Long recordId) {
        ExerciseRecordDto record = dashboardService.getRecordById(Long.parseLong(userId), recordId);
        return ResponseEntity.ok(record);
    }
}