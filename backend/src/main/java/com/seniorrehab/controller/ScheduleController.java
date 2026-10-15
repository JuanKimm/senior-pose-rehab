package com.seniorrehab.controller;

import com.seniorrehab.model.dto.ScheduleDto;
import com.seniorrehab.service.ScheduleService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;
import java.util.List;

@RestController
@RequestMapping("/api/notification")
@RequiredArgsConstructor
public class ScheduleController {

    private final ScheduleService scheduleService;

    // 일정 목록 조회
    @GetMapping("/schedule")
    public ResponseEntity<List<ScheduleDto>> getSchedules(
            @AuthenticationPrincipal String userId) {
        List<ScheduleDto> schedules = scheduleService.getSchedules(Long.parseLong(userId));
        return ResponseEntity.ok(schedules);
    }

    // 일정 등록
    @PostMapping("/schedule")
    public ResponseEntity<Void> createSchedule(
            @AuthenticationPrincipal String userId,
            @RequestBody ScheduleDto dto) {
        scheduleService.createSchedule(Long.parseLong(userId), dto);
        return ResponseEntity.ok().build();
    }

    // 일정 수정
    @PutMapping("/schedule/{id}")
    public ResponseEntity<Void> updateSchedule(
            @AuthenticationPrincipal String userId,
            @PathVariable Long id,
            @RequestBody ScheduleDto dto) {
        scheduleService.updateSchedule(Long.parseLong(userId), id, dto);
        return ResponseEntity.ok().build();
    }

    // 일정 삭제
    @DeleteMapping("/schedule/{id}")
    public ResponseEntity<Void> deleteSchedule(
            @AuthenticationPrincipal String userId,
            @PathVariable Long id) {
        scheduleService.deleteSchedule(Long.parseLong(userId), id);
        return ResponseEntity.ok().build();
    }

    // 알림 on/off
    @PutMapping("/schedule/{id}/toggle")
    public ResponseEntity<Void> toggleAlert(
            @AuthenticationPrincipal String userId,
            @PathVariable Long id) {
        scheduleService.toggleAlert(Long.parseLong(userId), id);
        return ResponseEntity.ok().build();
    }
}