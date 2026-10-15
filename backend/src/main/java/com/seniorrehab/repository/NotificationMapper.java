package com.seniorrehab.repository;

import com.seniorrehab.model.dto.NotiHistoryDto;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;
import java.util.List;
import java.time.LocalDateTime;

@Mapper
public interface NotificationMapper {
    List<NotiHistoryDto> findHistories(Long userId); // 알림 내역 목록 조회
    NotiHistoryDto findHistoryById(@Param("userId") Long userId, @Param("notificationId") Long notificationId); // 알림 내역 단건 조회

    int insertNotification(
        @Param("userId") Long userId,
        @Param("sessionId") Long sessionId,
        @Param("notiType") String notiType,
        @Param("status") String status,
        @Param("targetTel") String targetTel,
        @Param("shareToken") String shareToken,
        @Param("tokenExpiresAt") LocalDateTime tokenExpiresAt
    ); // 알림 기록 저장
}