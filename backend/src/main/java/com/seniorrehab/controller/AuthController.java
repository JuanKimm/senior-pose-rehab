package com.seniorrehab.controller;

import com.seniorrehab.model.dto.LoginRequestDto;
import com.seniorrehab.model.dto.LoginResponseDto;
import com.seniorrehab.model.dto.RefreshTokenRequestDto;
import com.seniorrehab.model.dto.RefreshTokenResponseDto;
import com.seniorrehab.model.dto.SignupRequestDto;
import com.seniorrehab.model.dto.SignupResponseDto;
import com.seniorrehab.service.AuthService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;

import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.AuthenticationException;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.validation.FieldError;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;

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

    // 로그아웃 - 저장된 리프레시 토큰 삭제
    @PostMapping("/logout")
    public ResponseEntity<Void> logout(@AuthenticationPrincipal String userId) {
        try {
            authService.logout(Long.valueOf(userId));
        } catch (NumberFormatException ignored) {
            // 토큰 없이(비로그인 상태로) 호출된 경우 - 지울 게 없으니 그냥 무시
        }
        return ResponseEntity.ok().build();
    }

    // @Valid 검증 실패 시 (빈 값, 형식 안 맞음 등) -> 400
    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ResponseEntity<Map<String, String>> handleValidationException(MethodArgumentNotValidException e) {
        String message = e.getBindingResult().getFieldErrors().stream()
                .findFirst()
                .map(FieldError::getDefaultMessage)
                .orElse("입력값이 올바르지 않습니다.");
        return ResponseEntity.status(400).body(Map.of("error", message));
    }

    // 회원가입 실패 (중복 등) -> 400
    @ExceptionHandler(IllegalArgumentException.class)
    public ResponseEntity<Map<String, String>> handleIllegalArgument(IllegalArgumentException e) {
        return ResponseEntity.status(400)
                .body(Map.of("error", e.getMessage()));
    }

    // 로그인 실패 시 401 응답 - 전화번호/비번 틀리거나 사용자 없을 때
    @ExceptionHandler(AuthenticationException.class)
    public ResponseEntity<Map<String, String>> handleAuthException(AuthenticationException e) {
        return ResponseEntity.status(401)
                .body(Map.of("error", "전화번호 또는 비밀번호가 올바르지 않습니다."));
    }
}