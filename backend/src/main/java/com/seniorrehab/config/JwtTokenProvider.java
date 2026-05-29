package com.seniorrehab.config;

import io.jsonwebtoken.Claims;
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.security.Keys;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

import javax.crypto.SecretKey;
import java.nio.charset.StandardCharsets;
import java.util.Date;

@Component
public class JwtTokenProvider {

    private final SecretKey secretKey;
    private final long accessTokenValidity;

    // application.yml에서 secret, 만료시간을 읽어옴
    public JwtTokenProvider(
            @Value("${jwt.secret}") String secret,
            @Value("${jwt.access-token-validity}") long accessTokenValidity) {
        this.secretKey = Keys.hmacShaKeyFor(secret.getBytes(StandardCharsets.UTF_8));
        this.accessTokenValidity = accessTokenValidity;
    }

    // 토큰 생성 (로그인 성공 시 호출)
    public String createToken(String userId, String role) {
        Date now = new Date();
        Date expiry = new Date(now.getTime() + accessTokenValidity);

        return Jwts.builder()
                .subject(userId)          // 토큰 주인 (userId)
                .claim("role", role)      // 권한 정보 (USER 등)
                .issuedAt(now)            // 발급 시각
                .expiration(expiry)       // 만료 시각
                .signWith(secretKey)      // 비밀키로 서명
                .compact();
    }

    // 토큰에서 userId 꺼내기
    public String getUserId(String token) {
        return parseClaims(token).getSubject();
    }

    // 토큰에서 role 꺼내기
    public String getRole(String token) {
        return parseClaims(token).get("role", String.class);
    }

    // 토큰이 유효한지 검증
    public boolean validateToken(String token) {
        try {
            parseClaims(token);   // 파싱 성공하면 유효한 토큰
            return true;
        } catch (Exception e) {
            return false;         // 만료됐거나 위조됐거나 등
        }
    }

    // 토큰 내용 꺼내는 내부용 메서드
    private Claims parseClaims(String token) {
        return Jwts.parser()
                .verifyWith(secretKey)
                .build()
                .parseSignedClaims(token)
                .getPayload();
    }
}