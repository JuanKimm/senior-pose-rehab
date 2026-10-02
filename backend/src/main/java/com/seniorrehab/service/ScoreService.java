package com.seniorrehab.service;

import com.seniorrehab.repository.SessionMapper;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;


// AI 연동
@Service
@RequiredArgsConstructor
public class ScoreService {

    private final SessionMapper sessionMapper;

    // 스켈레톤 오버레이 영상 저장
    public boolean uploadVideo(Long sessionId, String videoPath) {
        if (sessionMapper.findSessionById(sessionId) == null) {
            return false;
        }
        sessionMapper.updateVideoPath(sessionId, videoPath);
        return true;
    }
}