package com.seniorrehab.controller;

import com.seniorrehab.model.dto.NotiHistoryDto;
import com.seniorrehab.service.NotificationService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;
import java.util.List;

@RestController
@RequestMapping("/api/notification")
@RequiredArgsConstructor
public class NotificationController {

    private final NotificationService notificationService;

    // 알림 내역 목록 조회
    @GetMapping("/history")
    public ResponseEntity<List<NotiHistoryDto>> getHistories(
            @AuthenticationPrincipal String userId) {
        List<NotiHistoryDto> histories = notificationService.getHistories(Long.parseLong(userId));
        return ResponseEntity.ok(histories);
    }

    // 알림 내역 단건 조회
    @GetMapping("/history/{id}")
    public ResponseEntity<NotiHistoryDto> getHistoryById(
            @AuthenticationPrincipal String userId,
            @PathVariable Long id) {
        NotiHistoryDto history = notificationService.getHistoryById(Long.parseLong(userId), id);
        return ResponseEntity.ok(history);
    }

    // 운동 일정 알림 발송
    @PostMapping("/send/schedule")
    public ResponseEntity<Void> sendScheduleAlarm() {
        notificationService.sendScheduleAlarm();
        return ResponseEntity.ok().build();
    }

    // 운동 결과 알림 발송
    @PostMapping("/send/result")
    public ResponseEntity<Void> sendResultAlarm(@RequestParam Long sessionId) {
        notificationService.sendResultAlarm(sessionId);
        return ResponseEntity.ok().build();
    }
}