package com.seniorrehab.service;

import com.seniorrehab.config.CustomUserDetails;
import com.seniorrehab.config.JwtTokenProvider;
import com.seniorrehab.model.dto.LoginRequestDto;
import com.seniorrehab.model.dto.LoginResponseDto;
import com.seniorrehab.model.entity.User;
import lombok.RequiredArgsConstructor;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.Authentication;
import org.springframework.stereotype.Service;

@Service
@RequiredArgsConstructor
public class AuthService {

    private final AuthenticationManager authenticationManager;
    private final JwtTokenProvider jwtTokenProvider;

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
}