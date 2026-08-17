package com.seniorrehab.repository;

import com.seniorrehab.model.dto.NotiHistoryDto;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;
import java.util.List;

@Mapper
public interface NotificationMapper {
    List<NotiHistoryDto> findHistories(Long userId); // 알림 내역 목록 조회
    NotiHistoryDto findHistoryById(@Param("userId") Long userId, @Param("notificationId") Long notificationId); // 알림 내역 단건 조회
}