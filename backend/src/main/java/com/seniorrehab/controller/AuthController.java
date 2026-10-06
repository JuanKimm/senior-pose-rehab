package com.seniorrehab.controller;

import com.seniorrehab.model.dto.CheckPhoneResponseDto;
import com.seniorrehab.model.dto.LoginRequestDto;
import com.seniorrehab.model.dto.LoginResponseDto;
import com.seniorrehab.model.dto.RefreshTokenRequestDto;
import com.seniorrehab.model.dto.RefreshTokenResponseDto;
import com.seniorrehab.model.dto.SignupRequestDto;
import com.seniorrehab.model.dto.SignupResponseDto;
import com.seniorrehab.model.dto.SmsSendRequestDto;
import com.seniorrehab.model.dto.SmsVerifyRequestDto;
import com.seniorrehab.model.dto.GuardianTokenResponseDto;
import com.seniorrehab.model.dto.FindPasswordRequestDto;
import com.seniorrehab.service.AuthService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;

import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/auth")
@RequiredArgsConstructor
public class AuthController {

    private final AuthService authService;

    // 회원가입
    @PostMapping("/signup")
    public ResponseEntity<SignupResponseDto> signup(@Valid @RequestBody SignupRequestDto request) {
        SignupResponseDto response = authService.signup(request);
        return ResponseEntity.status(HttpStatus.CREATED).body(response);   // 201 Created
    }

    // 전화번호 중복 확인
    @GetMapping("/check-phone/{tel}")
    public ResponseEntity<CheckPhoneResponseDto> checkPhone(@PathVariable String tel) {
        CheckPhoneResponseDto response = authService.checkPhone(tel);
        return ResponseEntity.ok(response);
    }

    // 인증코드 발송
    @PostMapping("/sms/send")
    public ResponseEntity<Void> sendSms(@Valid @RequestBody SmsSendRequestDto request) {
        authService.sendVerificationCode(request.getTel());
        return ResponseEntity.ok().build();
    }

    // 인증코드 확인
    @PostMapping("/sms/verify")
    public ResponseEntity<Void> verifySms(@Valid @RequestBody SmsVerifyRequestDto request) {
        authService.verifyCode(request.getTel(), request.getCode());
        return ResponseEntity.ok().build();
    }

    // 비밀번호 찾기
    @PostMapping("/find-password")
    public ResponseEntity<Void> findPassword(@Valid @RequestBody FindPasswordRequestDto request) {
        authService.findPassword(request.getTel(), request.getName());
        return ResponseEntity.ok().build();
    }
    
    // 로그인
    @PostMapping("/login")
    public ResponseEntity<LoginResponseDto> login(@Valid @RequestBody LoginRequestDto request) {
        LoginResponseDto response = authService.login(request);
        return ResponseEntity.ok(response);
    }

    // 토큰 갱신
    @PostMapping("/refresh-token")
    public ResponseEntity<RefreshTokenResponseDto> refresh(@Valid @RequestBody RefreshTokenRequestDto request) {
        RefreshTokenResponseDto response = authService.refresh(request);
        return ResponseEntity.ok(response);
    }

    // 보호자 일회성 링크 토큰 검증
    @PostMapping("/guardian-token/{token}")
    public ResponseEntity<GuardianTokenResponseDto> verifyGuardianToken(@PathVariable String token) {
        GuardianTokenResponseDto response = authService.verifyGuardianToken(token);
        return ResponseEntity.ok(response);
    }

    // 로그아웃 - 저장된 리프레시 토큰 삭제
    @PostMapping("/logout")
    public ResponseEntity<Void> logout(@AuthenticationPrincipal String userId) {
        try {
            authService.logout(Long.valueOf(userId));
        } catch (NumberFormatException ignored) {
            // 토큰 없이(비로그인 상태로) 호출된 경우
        }
        return ResponseEntity.ok().build();
    }
}