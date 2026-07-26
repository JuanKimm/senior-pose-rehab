package com.seniorrehab.service;

import com.seniorrehab.model.dto.ExerciseRecordDto;
import com.seniorrehab.repository.DashboardMapper;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

@Service
@RequiredArgsConstructor
public class DashboardService {

    private final DashboardMapper dashboardMapper;

    // 오늘 운동 기록 조회
    public ExerciseRecordDto getTodayRecord(Long userId) {
        return dashboardMapper.findTodayRecord(userId);
    }

}