package com.seniorrehab.repository;

import com.seniorrehab.model.entity.RefreshToken;
import org.apache.ibatis.annotations.Delete;
import org.apache.ibatis.annotations.Insert;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Select;

@Mapper
public interface RefreshTokenMapper {

    // 로그인 시 저장 - 이미 있으면 덮어쓰기(UPSERT), 없으면 새로 추가
    @Insert("INSERT INTO REFRESH_TOKEN (user_id, token, expired_at) " +
            "VALUES (#{userId}, #{token}, #{expiredAt}) " +
            "ON DUPLICATE KEY UPDATE token = #{token}, expired_at = #{expiredAt}")
    void upsertToken(RefreshToken refreshToken);

    // 토큰 갱신 시 - DB에 저장된 값과 클라이언트가 보낸 값이 같은지 대조용
    @Select("SELECT * FROM REFRESH_TOKEN WHERE user_id = #{userId}")
    RefreshToken findByUserId(Long userId);

    // 로그아웃 시 삭제
    @Delete("DELETE FROM REFRESH_TOKEN WHERE user_id = #{userId}")
    void deleteByUserId(Long userId);
}