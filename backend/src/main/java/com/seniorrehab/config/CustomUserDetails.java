package com.seniorrehab.config;

import com.seniorrehab.model.entity.User;
import lombok.RequiredArgsConstructor;
import org.springframework.security.core.GrantedAuthority;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.core.userdetails.UserDetails;

import java.util.Collection;
import java.util.List;

@RequiredArgsConstructor
public class CustomUserDetails implements UserDetails {

    private final User user;

    // 권한 목록
    @Override
    public Collection<? extends GrantedAuthority> getAuthorities() {
        return List.of(new SimpleGrantedAuthority(user.getRole()));
    }

    // 비밀번호 (DB의 암호화된 값)
    @Override
    public String getPassword() {
        return user.getPassword();
    }

    // 로그인 아이디 (전화번호)
    @Override
    public String getUsername() {
        return user.getTel();
    }

    // 계정 상태
    @Override
    public boolean isAccountNonExpired()     { return true; }
    @Override
    public boolean isAccountNonLocked()      { return true; }
    @Override
    public boolean isCredentialsNonExpired() { return true; }

    // 활성 여부 (탈퇴한 사용자는 false로 로그인 차단)
    @Override
    public boolean isEnabled() {
        return "ACTIVE".equals(user.getStatus());
    }

    // 원본 User 객체가 필요한 곳에서 쓸 수 있게 설정
    public User getUser() {
        return user;
    }
}