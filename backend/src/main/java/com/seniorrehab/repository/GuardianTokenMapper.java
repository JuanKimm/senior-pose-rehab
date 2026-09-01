package com.seniorrehab.repository;

import com.seniorrehab.model.dto.ShareTokenInfoDto;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

@Mapper
public interface GuardianTokenMapper {

    // share_token으로 NOTIFICATION 테이블 조회
    ShareTokenInfoDto findByShareToken(@Param("shareToken") String shareToken);
}