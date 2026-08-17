package com.seniorrehab.service;

import com.seniorrehab.model.dto.AccuracyGraphDto;
import com.seniorrehab.model.dto.BodyPartStatsDto;
import com.seniorrehab.model.dto.ExerciseRecordDto;
import com.seniorrehab.model.dto.FeedbackDto;
import com.seniorrehab.model.dto.MonthlySummaryDto;
import com.seniorrehab.repository.DashboardMapper;
import lombok.RequiredArgsConstructor;

import java.time.LocalDate;
import java.time.temporal.ChronoUnit;
import java.util.ArrayList;
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

    // 월간 요약 조회
    public MonthlySummaryDto getMonthlySummary(Long userId, int year, int month) {
        return dashboardMapper.findMonthlySummary(userId, year, month);
    }

    // 날짜별 정확도 그래프 조회
    public List<AccuracyGraphDto> getAccuracyGraph(Long userId) {
        return dashboardMapper.findAccuracyGraph(userId);
    }

    // 부위별 통계 조회
    public List<BodyPartStatsDto> getBodyPartStats(Long userId, int year, int month) {
        return dashboardMapper.findBodyPartStats(userId, year, month);
    }

    // 피드백 조회
    public List<FeedbackDto> getFeedback(Long userId) {
        List<FeedbackDto> feedbacks = new ArrayList<>();
        LocalDate now = LocalDate.now();
        int year = now.getYear();
        int month = now.getMonthValue();

        // 1. 마지막 운동 날짜
        LocalDate lastDate = dashboardMapper.findLastExerciseDate(userId);
        if (lastDate != null) {
            long daysSinceLast = ChronoUnit.DAYS.between(lastDate, now);
            if (daysSinceLast >= 3) {
                FeedbackDto dto = new FeedbackDto();
                dto.setMessage("오늘 운동 어떠세요? 꾸준한 운동이 재활에 도움이 됩니다 😊");
                dto.setType("FREQUENCY");
                feedbacks.add(dto);
            }
        }

        // 2. 이번 달 운동 일수
        Integer monthlyDays = dashboardMapper.findMonthlyExerciseDays(userId, year, month);
        if (monthlyDays != null && monthlyDays >= 10) {
            FeedbackDto dto = new FeedbackDto();
            dto.setMessage("이번 달 꾸준히 운동하고 계시네요! 훌륭해요 💪");
            dto.setType("FREQUENCY");
            feedbacks.add(dto);
        }

        // 3. 연속 운동 일수
        Integer consecutiveDays = dashboardMapper.findConsecutiveDays(userId);
        if (consecutiveDays != null && consecutiveDays >= 3) {
            FeedbackDto dto = new FeedbackDto();
            dto.setMessage("연속으로 운동하고 계시네요! 대단해요 🔥");
            dto.setType("FREQUENCY");
            feedbacks.add(dto);
        }

        // 4. 전월 대비 정확도 향상
        MonthlySummaryDto thisMonth = dashboardMapper.findMonthlySummary(userId, year, month);
        MonthlySummaryDto lastMonth = dashboardMapper.findMonthlySummary(userId, year, month - 1);
        if (thisMonth != null && lastMonth != null &&
            thisMonth.getAvgAccuracy() != null && lastMonth.getAvgAccuracy() != null) {
            float improvement = thisMonth.getAvgAccuracy() - lastMonth.getAvgAccuracy();
            if (improvement >= 5) {
                FeedbackDto dto = new FeedbackDto();
                dto.setMessage("지난달보다 정확도가 향상됐어요! 계속 이대로 해보세요 👍");
                dto.setType("ACCURACY");
                feedbacks.add(dto);
            }
        }

        // 5. 평균 정확도 90% 이상
        if (thisMonth != null && thisMonth.getAvgAccuracy() != null) {
            if (thisMonth.getAvgAccuracy() >= 90) {
                FeedbackDto dto = new FeedbackDto();
                dto.setMessage("정확도가 아주 높아요! 훌륭한 자세입니다 ✨");
                dto.setType("ACCURACY");
                feedbacks.add(dto);
            } else if (thisMonth.getAvgAccuracy() < 60) {
                FeedbackDto dto = new FeedbackDto();
                dto.setMessage("자세를 조금 더 신경써보세요. 천천히 해도 괜찮아요 😊");
                dto.setType("ACCURACY");
                feedbacks.add(dto);
            }
        }

        // 6. 부위 관련
        List<String> bodyParts = dashboardMapper.findMonthlyBodyParts(userId, year, month);
        List<String> allParts = List.of("상체", "어깨", "하체");

        if (bodyParts != null) {
            // 이번 달 모든 부위 운동
            if (bodyParts.containsAll(allParts)) {
                FeedbackDto dto = new FeedbackDto();
                dto.setMessage("이번 달 상체, 어깨, 하체 모두 운동하셨네요! 균형 잡힌 재활을 하고 계세요 🌟");
                dto.setType("BODY_PART");
                feedbacks.add(dto);
            }
            // 한 부위만 계속 운동
            else if (bodyParts.size() == 1) {
                FeedbackDto dto = new FeedbackDto();
                dto.setMessage(bodyParts.get(0) + " 운동을 꾸준히 하고 계시네요! 다른 부위도 함께 해보는 건 어떨까요?");
                dto.setType("BODY_PART");
                feedbacks.add(dto);
            }
            // 오랫동안 안 한 부위 있음
            else {
                for (String part : allParts) {
                    if (!bodyParts.contains(part)) {
                        FeedbackDto dto = new FeedbackDto();
                        dto.setMessage(part + " 운동을 한동안 안 하셨네요. 균형 잡힌 재활을 위해 함께 해보세요 💙");
                        dto.setType("BODY_PART");
                        feedbacks.add(dto);
                    }
                }
            }
        }

        return feedbacks;
    }

    // 영상 경로 조회
    public String getVideoPath(Long userId, Long sessionId) {
        return dashboardMapper.findVideoPathBySessionId(userId, sessionId);
    }

    // 월별 운동 날짜 조회
    public List<LocalDate> getCalendarDates(Long userId, int year, int month) {
        return dashboardMapper.findCalendarDates(userId, year, month);
    }

    // 날짜별 기록 팝업 조회
    public ExerciseRecordDto getCalendarRecord(Long userId, String date) {
        return dashboardMapper.findCalendarRecord(userId, date);
    }

    // 연속 운동일 조회
    public Integer getStreakDays(Long userId) {
        return dashboardMapper.findStreakDays(userId);
    }
}