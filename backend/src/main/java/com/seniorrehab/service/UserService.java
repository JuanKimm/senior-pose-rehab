package com.seniorrehab.service;

import com.seniorrehab.model.dto.UserInfoResponseDto;
import com.seniorrehab.model.entity.User;
import com.seniorrehab.repository.UserMapper;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

@Service
@RequiredArgsConstructor
public class UserService {

    private final UserMapper userMapper;

    // 내 정보 조회
    public UserInfoResponseDto getMyInfo(Long userId) {
        User user = userMapper.findByUserId(userId);

        return UserInfoResponseDto.builder()
                .name(user.getName())
                .tel(user.getTel())
                .guardianTel(user.getGuardianTel())
                .build();
    }
}