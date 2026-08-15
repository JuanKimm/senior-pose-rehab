package com.seniorrehab.service;

import com.seniorrehab.model.dto.ExerciseRecordDto;
import com.seniorrehab.repository.DashboardMapper;
import lombok.RequiredArgsConstructor;
import java.util.List;
import org.springframework.stereotype.Service;

@Service
@RequiredArgsConstructor
public class DashboardService {
    private final DashboardMapper dashboardMapper;

    // 오늘 운동 기록 조회
    public ExerciseRecordDto getTodayRecord(Long userId) {
        return dashboardMapper.findTodayRecord(userId);
    }

    // 최근 7일 운동 기록 조회
    public List<ExerciseRecordDto> getRecentRecords(Long userId) {
        return dashboardMapper.findRecentRecords(userId);
    }

    // 전체 운동 기록 조회
    public List<ExerciseRecordDto> getAllRecords(Long userId) {
        return dashboardMapper.findAllRecords(userId);
    }

    // 특정 날짜 운동 기록 조회
    public List<ExerciseRecordDto> getRecordsByDate(Long userId, String date) {
        return dashboardMapper.findRecordsByDate(userId, date);
    }

    // 운동 기록 단건 상세 조회
    public ExerciseRecordDto getRecordById(Long userId, Long sessionId) {
        return dashboardMapper.findRecordById(userId, sessionId);
    }
}