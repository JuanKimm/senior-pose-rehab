package com.seniorrehab.config;

import com.seniorrehab.model.entity.User;
import com.seniorrehab.repository.UserMapper;
import lombok.RequiredArgsConstructor;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.security.core.userdetails.UserDetailsService;
import org.springframework.security.core.userdetails.UsernameNotFoundException;
import org.springframework.stereotype.Service;

// 로그인 시 DB에서 사용자를 찾아오는 서비스
@Service
@RequiredArgsConstructor
public class CustomUserDetailsService implements UserDetailsService {

    private final UserMapper userMapper;

    @Override
    public UserDetails loadUserByUsername(String tel) throws UsernameNotFoundException {

        // 1. DB에서 전화번호로 유저 검색
        User user = userMapper.findByTel(tel);

        // 2. 없으면 예외 발생
        if (user == null) {
            throw new UsernameNotFoundException("해당 전화번호로 등록된 사용자가 없습니다: " + tel);
        }

        // 3. User를 CustomUserDetails로 포장해서 반환
        return new CustomUserDetails(user);
    }
}