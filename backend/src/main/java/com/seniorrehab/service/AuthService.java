package com.seniorrehab.service;

import com.seniorrehab.config.CustomUserDetails;
import com.seniorrehab.config.JwtTokenProvider;
import com.seniorrehab.model.dto.CheckPhoneResponseDto;
import com.seniorrehab.model.dto.LoginRequestDto;
import com.seniorrehab.model.dto.LoginResponseDto;
import com.seniorrehab.model.dto.RefreshTokenRequestDto;
import com.seniorrehab.model.dto.RefreshTokenResponseDto;
import com.seniorrehab.model.dto.SignupRequestDto;
import com.seniorrehab.model.dto.SignupResponseDto;
import com.seniorrehab.model.entity.RefreshToken;
import com.seniorrehab.model.entity.User;
import com.seniorrehab.repository.RefreshTokenMapper;
import com.seniorrehab.repository.UserMapper;
import com.seniorrehab.repository.VerificationCodeRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.Authentication;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.time.ZoneId;
import java.util.Date;
import java.util.concurrent.ThreadLocalRandom;

@Service
@RequiredArgsConstructor
public class AuthService {

    private final AuthenticationManager authenticationManager;
    private final JwtTokenProvider jwtTokenProvider;
    private final UserMapper userMapper;
    private final RefreshTokenMapper refreshTokenMapper;
    private final PasswordEncoder passwordEncoder;
    private final SmsService smsService;
    private final VerificationCodeRepository verificationCodeRepository;

    // 회원가입
    public SignupResponseDto signup(SignupRequestDto request) {

        // 1. 전화번호 중복 체크
        if (userMapper.countByTel(request.getTel()) > 0) {
            throw new IllegalArgumentException("이미 가입된 전화번호입니다.");
        }

        // 2. 전화번호 인증 완료 여부 확인
        if (!verificationCodeRepository.isVerified(request.getTel())) {
            throw new IllegalArgumentException("전화번호 인증을 먼저 완료해주세요.");
        }

        // 3. 비밀번호 BCrypt 암호화
        String encodedPassword = passwordEncoder.encode(request.getPassword());

        // 4. User 엔티티 만들기
        User user = new User();
        user.setTel(request.getTel());
        user.setPassword(encodedPassword);
        user.setName(request.getName());
        user.setGuardianTel(request.getGuardianTel());

        // 5. DB INSERT
        userMapper.insertUser(user);

        // 6. 인증 상태 초기화 - 재사용 방지
        verificationCodeRepository.clearVerified(request.getTel());

        // 7. 응답 DTO 반환
        return SignupResponseDto.builder()
                .userId(user.getUserId())
                .tel(user.getTel())
                .name(user.getName())
                .build();
    }

    // 전화번호 중복 확인
    public CheckPhoneResponseDto checkPhone(String tel) {
        boolean available = userMapper.countByTel(tel) == 0;
        return CheckPhoneResponseDto.builder()
                .avilable(available)
                .build();
    }

    // 인증코드 발송
    public void sendVerificationCode(String tel) {
        String code = generateCode();
        LocalDateTime expiredAt = LocalDateTime.now().plusMinutes(5);

        verificationCodeRepository.save(tel, code, expiredAt);

        System.out.println("[개발용 로그] " + tel + " 인증코드: " + code); // 테스트 -> Solapi 적용 시 삭제할 예정

        try {
            smsService.sendSms(tel, "[포즈온] 인증번호는 " + code + " 입니다. 5분 이내에 입력해주세요.");
        } catch (Exception e) {
            System.out.println("[SMS 발송 실패 - 더미 키 사용 중일 수 있음] " + e.getMessage());    // 테스트 -> Solapi 적용 시 삭제할 예정
        }
    }

    // 6자리 인증코드 생성
    private String generateCode() {
        int code = ThreadLocalRandom.current().nextInt(100000, 1000000);
        return String.valueOf(code);
    }

    // 인증코드 확인
    public void verifyCode(String tel, String code) {
        boolean valid = verificationCodeRepository.verify(tel, code);
        if (!valid) {
            throw new IllegalArgumentException("인증번호가 일치하지 않거나 만료되었습니다.");
        }

        // 인증 성공 - 회원가입 때 확인할 수 있도록 표시해둠
        verificationCodeRepository.markVerified(tel);
    }

    // 로그인
    public LoginResponseDto login(LoginRequestDto request) {

        // 1. 인증 시도
        Authentication authentication = authenticationManager.authenticate(
                new UsernamePasswordAuthenticationToken(request.getTel(), request.getPassword())
        );

        // 2. 인증된 유저 정보 꺼내기
        CustomUserDetails userDetails = (CustomUserDetails) authentication.getPrincipal();
        User user = userDetails.getUser();

        // 3. 액세스 토큰 + 리프레시 토큰 생성
        String accessToken = jwtTokenProvider.createToken(
                String.valueOf(user.getUserId()),
                user.getRole()
        );
        String refreshToken = jwtTokenProvider.createRefreshToken(
                String.valueOf(user.getUserId())
        );

        // 4. 리프레시 토큰 DB에 저장 (기존 것 있으면 덮어씀)
        RefreshToken tokenEntity = new RefreshToken();
        tokenEntity.setUserId(user.getUserId());
        tokenEntity.setToken(refreshToken);
        tokenEntity.setExpiredAt(toLocalDateTime(jwtTokenProvider.getExpiration(refreshToken)));
        refreshTokenMapper.upsertToken(tokenEntity);

        // 5. 응답 DTO에 담아 반환
        return LoginResponseDto.builder()
                .accessToken(accessToken)
                .refreshToken(refreshToken)
                .userId(user.getUserId())
                .name(user.getName())
                .tel(user.getTel())
                .role(user.getRole())
                .build();
    }

    // 토큰 갱신
    public RefreshTokenResponseDto refresh(RefreshTokenRequestDto request) {

        String refreshToken = request.getRefreshToken();

        // 1. 서명/만료 검증
        if (!jwtTokenProvider.validateToken(refreshToken)) {
            throw new IllegalArgumentException("리프레시 토큰이 만료되었거나 유효하지 않습니다. 다시 로그인해주세요.");
        }

        // 2. 액세스 토큰을 잘못 넣은 경우 방지 (반드시 refresh 타입이어야 함)
        if (!"refresh".equals(jwtTokenProvider.getTokenType(refreshToken))) {
            throw new IllegalArgumentException("유효하지 않은 토큰 형식입니다.");
        }

        // 3. DB에 저장된 값과 일치하는지 확인 (로그아웃 등으로 무효화됐는지 체크)
        Long userId = Long.valueOf(jwtTokenProvider.getUserId(refreshToken));
        RefreshToken saved = refreshTokenMapper.findByUserId(userId);

        if (saved == null || !saved.getToken().equals(refreshToken)) {
            throw new IllegalArgumentException("이미 로그아웃되었거나 무효화된 토큰입니다. 다시 로그인해주세요.");
        }

        // 4. 유저 정보 조회
        User user = userMapper.findByUserId(userId);

        // 5. 새 액세스 토큰 발급
        String newAccessToken = jwtTokenProvider.createToken(
                String.valueOf(user.getUserId()),
                user.getRole()
        );

        return RefreshTokenResponseDto.builder()
                .accessToken(newAccessToken)
                .build();
    }

    // 로그아웃 - 저장된 리프레시 토큰 삭제
    public void logout(Long userId) {
        refreshTokenMapper.deleteByUserId(userId);
    }

    // Date -> LocalDateTime 변환 (DB 저장용)
    private LocalDateTime toLocalDateTime(Date date) {
        return date.toInstant().atZone(ZoneId.systemDefault()).toLocalDateTime();
    }
}