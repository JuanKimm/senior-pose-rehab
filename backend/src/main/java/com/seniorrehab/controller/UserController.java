package com.seniorrehab.controller;

import com.seniorrehab.model.dto.UpdateUserRequestDto;
import com.seniorrehab.model.dto.UserInfoResponseDto;
import com.seniorrehab.service.UserService;

import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/user")
@RequiredArgsConstructor
public class UserController {

    private final UserService userService;

    // 내 정보 조회
    @GetMapping("/me")
    public ResponseEntity<UserInfoResponseDto> getMyInfo(@AuthenticationPrincipal String userId) {
        UserInfoResponseDto response = userService.getMyInfo(Long.parseLong(userId));
        return ResponseEntity.ok(response);
    }

    // 내 정보 수정
    @PutMapping("/me")
    public ResponseEntity<UserInfoResponseDto> updateMyInfo(
            @AuthenticationPrincipal String userId,
            @Valid @RequestBody UpdateUserRequestDto request) {
        UserInfoResponseDto response = userService.updateMyInfo(Long.parseLong(userId), request);
        return ResponseEntity.ok(response);
    }
}