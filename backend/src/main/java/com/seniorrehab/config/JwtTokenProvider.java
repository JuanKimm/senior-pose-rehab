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
    private final long refreshTokenValidity;

    // application.yml에서 secret, 만료시간을 읽어옴
    public JwtTokenProvider(
            @Value("${jwt.secret}") String secret,
            @Value("${jwt.access-token-validity}") long accessTokenValidity,
            @Value("${jwt.refresh-token-validity}") long refreshTokenValidity) {
        this.secretKey = Keys.hmacShaKeyFor(secret.getBytes(StandardCharsets.UTF_8));
        this.accessTokenValidity = accessTokenValidity;
        this.refreshTokenValidity = refreshTokenValidity;
    }

    // 액세스 토큰 생성 (로그인 성공 시 호출)
    public String createToken(String userId, String role) {
        Date now = new Date();
        Date expiry = new Date(now.getTime() + accessTokenValidity);

        return Jwts.builder()
                .subject(userId)
                .claim("role", role)
                .claim("tokenType", "access")   // 액세스/리프레시 구분용
                .issuedAt(now)
                .expiration(expiry)
                .signWith(secretKey)
                .compact();
    }

    // 리프레시 토큰 생성 (로그인 성공 시 호출)
    public String createRefreshToken(String userId) {
        Date now = new Date();
        Date expiry = new Date(now.getTime() + refreshTokenValidity);

        return Jwts.builder()
                .subject(userId)
                .claim("tokenType", "refresh")  // role은 안 담음 - 액세스 토큰 재발급 때만 씀
                .issuedAt(now)
                .expiration(expiry)
                .signWith(secretKey)
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

    // 토큰 종류 꺼내기 ("access" 또는 "refresh")
    public String getTokenType(String token) {
        return parseClaims(token).get("tokenType", String.class);
    }

    // 토큰 만료 시각 꺼내기 (DB 저장용)
    public Date getExpiration(String token) {
        return parseClaims(token).getExpiration();
    }

    // 토큰이 유효한지 검증 (서명 + 만료시간)
    public boolean validateToken(String token) {
        try {
            parseClaims(token);
            return true;
        } catch (Exception e) {
            return false;
        }
    }

    private Claims parseClaims(String token) {
        return Jwts.parser()
                .verifyWith(secretKey)
                .build()
                .parseSignedClaims(token)
                .getPayload();
    }
}