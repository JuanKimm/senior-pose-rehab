package com.seniorrehab.service;

import com.seniorrehab.model.dto.UpdateUserRequestDto;
import com.seniorrehab.model.dto.UserInfoResponseDto;
import com.seniorrehab.model.entity.User;
import com.seniorrehab.repository.UserMapper;
import com.seniorrehab.repository.VerificationCodeRepository;

import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

@Service
@RequiredArgsConstructor
public class UserService {

    private final UserMapper userMapper;
    private final VerificationCodeRepository verificationCodeRepository;

    // 내 정보 조회
    public UserInfoResponseDto getMyInfo(Long userId) {
        User user = userMapper.findByUserId(userId);

        return UserInfoResponseDto.builder()
                .name(user.getName())
                .tel(user.getTel())
                .guardianTel(user.getGuardianTel())
                .build();
    }

    // 내 정보 수정
    public UserInfoResponseDto updateMyInfo(Long userId, UpdateUserRequestDto request) {

        // 1. 새 전화번호가 다른 유저와 중복되는지 확인
        if (userMapper.countByTelExcludingUser(request.getTel(), userId) > 0) {
            throw new IllegalArgumentException("이미 사용 중인 전화번호입니다.");
        }

        // 2. 전화번호를 실제로 바꾸는 경우에만 인증 여부 확인
        User current = userMapper.findByUserId(userId);
        boolean telChanged = !current.getTel().equals(request.getTel());

        if (telChanged && !verificationCodeRepository.isVerified(request.getTel())) {
            throw new IllegalArgumentException("변경할 전화번호의 인증을 먼저 완료해주세요.");
        }

        // 3. 정보 수정
        userMapper.updateUserInfo(userId, request.getTel(), request.getName(), request.getGuardianTel());

        // 4. 인증 상태 초기화 (재사용 방지) - 전화번호를 바꾼 경우에만
        if (telChanged) {
            verificationCodeRepository.clearVerified(request.getTel());
        }

        // 5. 수정된 정보 다시 조회해서 반환
        User updated = userMapper.findByUserId(userId);
        return toResponseDto(updated);
    }

    // User 엔티티 -> 응답 DTO 변환 (중복 코드 방지용)
    private UserInfoResponseDto toResponseDto(User user) {
        return UserInfoResponseDto.builder()
                .name(user.getName())
                .tel(user.getTel())
                .guardianTel(user.getGuardianTel())
                .build();
    }
}