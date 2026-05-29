package com.seniorrehab.repository;

import com.seniorrehab.model.entity.User;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Select;

@Mapper
public interface UserMapper {

    @Select("SELECT * FROM USER WHERE tel = #{tel}")
    User findByTel(String tel);
}