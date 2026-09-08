package com.seniorrehab.repository;

import com.seniorrehab.model.entity.ExerciseSession;
import org.apache.ibatis.annotations.Mapper;

@Mapper
public interface SessionMapper {
    int insertSession(ExerciseSession session); // 운동 세션 시작
}