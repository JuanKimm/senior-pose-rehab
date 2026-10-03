package com.seniorrehab.repository;

import com.seniorrehab.model.dto.ScheduleDto;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;
import java.util.List;

@Mapper
public interface ScheduleMapper {
    List<ScheduleDto> findSchedules(Long userId); // 일정 목록 조회
    int insertSchedule(@Param("userId") Long userId, @Param("dto") ScheduleDto dto); // 일정 등록
    int updateSchedule(@Param("userId") Long userId, @Param("scheduleId") Long scheduleId, @Param("dto") ScheduleDto dto); // 일정 수정
    int deleteSchedule(@Param("userId") Long userId, @Param("scheduleId") Long scheduleId); // 일정 삭제
    int toggleAlert(@Param("userId") Long userId, @Param("scheduleId") Long scheduleId); // 알림 on/off
    List<ScheduleDto> findTodaySchedules(); // 오늘 발송할 일정 조회
}