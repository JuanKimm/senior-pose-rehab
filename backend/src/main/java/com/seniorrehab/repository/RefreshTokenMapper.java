package com.seniorrehab.repository;

import com.seniorrehab.model.entity.RefreshToken;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

@Mapper
public interface RefreshTokenMapper {

    // 로그인 시 저장 - 이미 있으면 덮어쓰기(UPSERT), 없으면 새로 추가
    void upsertToken(@Param("refreshToken") RefreshToken refreshToken);

    // 토큰 갱신 시 - DB에 저장된 값과 클라이언트가 보낸 값이 같은지 대조용
    RefreshToken findByUserId(@Param("userId") Long userId);

    // 로그아웃 시 삭제
    void deleteByUserId(@Param("userId") Long userId);
}