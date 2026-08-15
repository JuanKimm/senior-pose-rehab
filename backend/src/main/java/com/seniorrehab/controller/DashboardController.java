package com.seniorrehab.controller;

import com.seniorrehab.model.dto.AccuracyGraphDto;
import com.seniorrehab.model.dto.BodyPartStatsDto;
import com.seniorrehab.model.dto.ExerciseRecordDto;
import com.seniorrehab.model.dto.MonthlySummaryDto;
import com.seniorrehab.service.DashboardService;
import lombok.RequiredArgsConstructor;

import java.time.LocalDate;
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

    // 이번 달 요약 조회
    @GetMapping("/monthly-summary")
    public ResponseEntity<MonthlySummaryDto> getMonthlySummary(
            @AuthenticationPrincipal String userId) {
        LocalDate now = LocalDate.now();
        MonthlySummaryDto summary = dashboardService.getMonthlySummary(
                Long.parseLong(userId), now.getYear(), now.getMonthValue());
        return ResponseEntity.ok(summary);
    }

    // 특정 월 요약 조회
    @GetMapping("/monthly-summary/{year}/{month}")
    public ResponseEntity<MonthlySummaryDto> getMonthlySummaryByYearMonth(
            @AuthenticationPrincipal String userId,
            @PathVariable int year,
            @PathVariable int month) {
        MonthlySummaryDto summary = dashboardService.getMonthlySummary(
                Long.parseLong(userId), year, month);
        return ResponseEntity.ok(summary);
    }

    // 날짜별 정확도 그래프 조회
    @GetMapping("/accuracy-graph")
    public ResponseEntity<List<AccuracyGraphDto>> getAccuracyGraph(
            @AuthenticationPrincipal String userId) {
        List<AccuracyGraphDto> graph = dashboardService.getAccuracyGraph(Long.parseLong(userId));
        return ResponseEntity.ok(graph);
    }

    // 부위별 통계 조회
    @GetMapping("/stats/body-parts")
    public ResponseEntity<List<BodyPartStatsDto>> getBodyPartStats(
            @AuthenticationPrincipal String userId,
            @RequestParam(defaultValue = "#{T(java.time.LocalDate).now().getYear()}") int year,
            @RequestParam(defaultValue = "#{T(java.time.LocalDate).now().getMonthValue()}") int month) {
        List<BodyPartStatsDto> stats = dashboardService.getBodyPartStats(Long.parseLong(userId), year, month);
        return ResponseEntity.ok(stats);
    }
}