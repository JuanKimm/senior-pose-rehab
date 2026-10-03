package com.seniorrehab.service;

import com.seniorrehab.model.dto.ExerciseRecordDto;
import com.seniorrehab.model.dto.NotiHistoryDto;
import com.seniorrehab.model.dto.ScheduleDto;
import com.seniorrehab.repository.NotificationMapper;
import com.seniorrehab.repository.ScheduleMapper;
import com.seniorrehab.repository.DashboardMapper;

import lombok.RequiredArgsConstructor;

import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Service;
import java.util.List;
import java.util.UUID;

import java.time.LocalDateTime;

@Service
@RequiredArgsConstructor
public class NotificationService {

    private final NotificationMapper notificationMapper;
    private final ScheduleMapper scheduleMapper;
    private final DashboardMapper dashboardMapper;
    private final SmsService smsService;

    // 알림 내역 목록 조회
    public List<NotiHistoryDto> getHistories(Long userId) {
        return notificationMapper.findHistories(userId);
    }

    // 알림 내역 단건 조회
    public NotiHistoryDto getHistoryById(Long userId, Long notificationId) {
        return notificationMapper.findHistoryById(userId, notificationId);
    }

    // 운동 일정 알림 발송
    public void sendScheduleAlarm() {
        List<ScheduleDto> schedules = scheduleMapper.findTodaySchedules();
        
        for (ScheduleDto schedule : schedules) {
            String message = "[PoseOn] 안녕하세요, " + schedule.getName() + "님 :)\n" +
                "오늘 " + schedule.getExerciseTime() + "은 PoseOn 재활 운동 시간이에요!\n" +
                "지금 바로 시작해보세요!\n" +
                "→ http://localhost:5173";

            // 본인에게 발송
            try {
                smsService.sendSms(schedule.getTel(), message);
                saveNotification(schedule.getUserId(), null, "일정알림", "발송성공", schedule.getTel(), null, null);
            } catch (Exception e) {
                saveNotification(schedule.getUserId(), null, "일정알림", "발송실패", schedule.getTel(), null, null);
            }

            // 보호자에게 발송
            if (schedule.getGuardianTel() != null) {
                try {
                    smsService.sendSms(schedule.getGuardianTel(), message);
                    saveNotification(schedule.getUserId(), null, "일정알림", "발송성공", schedule.getGuardianTel(), null, null);
                } catch (Exception e) {
                    saveNotification(schedule.getUserId(), null, "일정알림", "발송실패", schedule.getGuardianTel(), null, null);
                }
            }
        }
    }

    // 알림 기록 저장
    private void saveNotification(Long userId, Long sessionId, String notiType, String status, String targetTel, String shareToken, LocalDateTime tokenExpiresAt) {
        notificationMapper.insertNotification(userId, sessionId, notiType, status, targetTel, shareToken, tokenExpiresAt);
    }

    // 매시간 실행 (TEST)
    // @Scheduled(cron = "0 0 * * * *") 
    public void scheduleAlarmJob() {
        sendScheduleAlarm();
    }

    // 운동 결과 알림 발송
    public void sendResultAlarm(Long sessionId) {
        ExerciseRecordDto record = dashboardMapper.findRecordWithUserBySessionId(sessionId);
        if (record == null) return;

        // 일회성 토큰 생성
        String token = UUID.randomUUID().toString();
        LocalDateTime tokenExpiresAt = LocalDateTime.now().plusHours(24);

        String message = "[PoseOn] " + record.getName() + "님이 오늘 운동을 완료했어요!\n" +
                "결과 확인하기 →\n" +
                "http://localhost:8080/api/exercise/result/share/" + token;

        // 본인에게 발송
        try {
            smsService.sendSms(record.getTel(), message);
            saveNotification(record.getUserId(), sessionId, "결과알림", "발송성공", record.getTel(), token, tokenExpiresAt);
        } catch (Exception e) {
            saveNotification(record.getUserId(), sessionId, "결과알림", "발송실패", record.getTel(), token, tokenExpiresAt);
        }

        // 보호자에게 발송
        if (record.getGuardianTel() != null) {
            try {
                smsService.sendSms(record.getGuardianTel(), message);
                saveNotification(record.getUserId(), sessionId, "결과알림", "발송성공", record.getGuardianTel(), token, tokenExpiresAt);
            } catch (Exception e) {
                saveNotification(record.getUserId(), sessionId, "결과알림", "발송실패", record.getGuardianTel(), token, tokenExpiresAt);
            }
        }
    }
}