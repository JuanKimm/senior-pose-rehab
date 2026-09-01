package com.seniorrehab.repository;

import com.seniorrehab.model.entity.User;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

@Mapper
public interface UserMapper {

    User findByTel(@Param("tel") String tel);   // 로그인 시 전화번호로 유저 조회
    int countByTel(@Param("tel") String tel);   // 전화번호 중복 체크
    int insertUser(@Param("user") User user);   // 회원가입
    User findByUserId(@Param("userId") Long userId);    // 토큰 갱신 시 userId로 유저 조회

    // 비밀번호 찾기 - 이름 + 전화번호 둘 다 일치해야 조회됨
    User findByTelAndName(@Param("tel") String tel, @Param("name") String name);
    
    // 비밀번호 찾기 - 임시 비밀번호로 업데이트
    int updatePassword(@Param("userId") Long userId, @Param("password") String password);
}