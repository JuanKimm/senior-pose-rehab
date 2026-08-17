package com.seniorrehab.service;

import com.seniorrehab.model.dto.ScheduleDto;
import com.seniorrehab.repository.ScheduleMapper;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import java.util.List;

@Service
@RequiredArgsConstructor
public class ScheduleService {

    private final ScheduleMapper scheduleMapper;

    // 일정 목록 조회
    public List<ScheduleDto> getSchedules(Long userId) {
        return scheduleMapper.findSchedules(userId);
    }

    // 일정 등록
    public void createSchedule(Long userId, ScheduleDto dto) {
        scheduleMapper.insertSchedule(userId, dto);
    }

    // 일정 수정
    public void updateSchedule(Long userId, Long scheduleId, ScheduleDto dto) {
        scheduleMapper.updateSchedule(userId, scheduleId, dto);
    }

    // 일정 삭제
    public void deleteSchedule(Long userId, Long scheduleId) {
        scheduleMapper.deleteSchedule(userId, scheduleId);
    }

    // 알림 on/off
    public void toggleAlert(Long userId, Long scheduleId) {
        scheduleMapper.toggleAlert(userId, scheduleId);
    }
}