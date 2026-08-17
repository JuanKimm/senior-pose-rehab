package com.seniorrehab.service;

import com.seniorrehab.model.dto.NotiHistoryDto;
import com.seniorrehab.repository.NotificationMapper;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import java.util.List;

@Service
@RequiredArgsConstructor
public class NotificationService {

    private final NotificationMapper notificationMapper;

    // 알림 내역 목록 조회
    public List<NotiHistoryDto> getHistories(Long userId) {
        return notificationMapper.findHistories(userId);
    }

    // 알림 내역 단건 조회
    public NotiHistoryDto getHistoryById(Long userId, Long notificationId) {
        return notificationMapper.findHistoryById(userId, notificationId);
    }
}