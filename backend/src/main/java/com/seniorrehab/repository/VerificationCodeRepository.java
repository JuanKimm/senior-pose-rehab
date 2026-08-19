package com.seniorrehab.repository;

import org.springframework.stereotype.Component;

import java.time.LocalDateTime;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

// 전화번호 인증코드를 서버 메모리에 잠깐 저장해두는 저장소
@Component
public class VerificationCodeRepository {

    private final Map<String, CodeEntry> store = new ConcurrentHashMap<>();

    // 인증코드 저장 (같은 번호로 다시 보내면 기존 코드는 자동으로 덮어써짐)
    public void save(String tel, String code, LocalDateTime expiredAt) {
        store.put(tel, new CodeEntry(code, expiredAt));
    }

    // 인증코드 확인 - 맞으면 true
    public boolean verify(String tel, String code) {
        CodeEntry entry = store.get(tel);

        if (entry == null) {
            return false;   // 발송된 적 없음
        }
        if (entry.expiredAt().isBefore(LocalDateTime.now())) {
            store.remove(tel);   // 만료됐으면 지워버림
            return false;
        }
        if (!entry.code().equals(code)) {
            return false;   // 코드 불일치
        }

        store.remove(tel);   // 검증 성공 - 재사용 못 하게 바로 삭제
        return true;
    }

    private record CodeEntry(String code, LocalDateTime expiredAt) {}
}