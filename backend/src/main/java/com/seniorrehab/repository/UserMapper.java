package com.seniorrehab.repository;

import com.seniorrehab.model.entity.User;

import org.apache.ibatis.annotations.Insert;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Options;
import org.apache.ibatis.annotations.Select;

@Mapper
public interface UserMapper {

    // 로그인 시 전화번호로 유저 조회
    @Select("SELECT * FROM USER WHERE tel = #{tel}")
    User findByTel(String tel);

    // 전화번호 중복 체크
    @Select("SELECT COUNT(*) FROM USER WHERE tel = #{tel}")
    int countByTel(String tel);

    // 회원가입
    @Insert("INSERT INTO USER (tel, password, name, guardian_tel) " +
            "VALUES (#{tel}, #{password}, #{name}, #{guardianTel})")
    @Options(useGeneratedKeys = true, keyProperty = "userId")
    int insertUser(User user);
}