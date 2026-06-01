package com.seniorrehab.service;

import com.seniorrehab.config.CustomUserDetails;
import com.seniorrehab.config.JwtTokenProvider;
import com.seniorrehab.model.dto.LoginRequestDto;
import com.seniorrehab.model.dto.LoginResponseDto;
import com.seniorrehab.model.dto.SignupRequestDto;
import com.seniorrehab.model.dto.SignupResponseDto;
import com.seniorrehab.model.entity.User;
import com.seniorrehab.repository.UserMapper;
import lombok.RequiredArgsConstructor;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.Authentication;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

@Service
@RequiredArgsConstructor
public class AuthService {

    private final AuthenticationManager authenticationManager;
    private final JwtTokenProvider jwtTokenProvider;
    private final UserMapper userMapper;
    private final PasswordEncoder passwordEncoder;

    // 로그인
    public LoginResponseDto login(LoginRequestDto request) {

        // 1. 인증 시도
        Authentication authentication = authenticationManager.authenticate(
                new UsernamePasswordAuthenticationToken(request.getTel(), request.getPassword())
        );

        // 2. 인증된 유저 정보 꺼내기
        CustomUserDetails userDetails = (CustomUserDetails) authentication.getPrincipal();
        User user = userDetails.getUser();

        // 3. JWT 토큰 생성
        String accessToken = jwtTokenProvider.createToken(
                String.valueOf(user.getUserId()),
                user.getRole()
        );

        // 4. 응답 DTO에 담아 반환
        return LoginResponseDto.builder()
                .accessToken(accessToken)
                .userId(user.getUserId())
                .name(user.getName())
                .tel(user.getTel())
                .role(user.getRole())
                .build();
    }

    // 회원가입
    public SignupResponseDto signup(SignupRequestDto request) {

        // 1. 전화번호 중복 체크
        if (userMapper.countByTel(request.getTel()) > 0) {
            throw new IllegalArgumentException("이미 가입된 전화번호입니다.");
        }

        // 2. 비밀번호 BCrypt 암호화
        String encodedPassword = passwordEncoder.encode(request.getPassword());

        // 3. User 엔티티 만들기 (role, status는 DB DEFAULT로 자동 설정)
        User user = new User();
        user.setTel(request.getTel());
        user.setPassword(encodedPassword);
        user.setName(request.getName());
        user.setGuardianTel(request.getGuardianTel());

        // 4. DB INSERT
        userMapper.insertUser(user);

        // 5. 응답 DTO 반환
        return SignupResponseDto.builder()
                .userId(user.getUserId())
                .tel(user.getTel())
                .name(user.getName())
                .build();
    }
}