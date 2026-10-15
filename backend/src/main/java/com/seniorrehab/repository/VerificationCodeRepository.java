package com.seniorrehab.repository;

import org.springframework.stereotype.Component;

import java.time.LocalDateTime;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

// 전화번호 인증코드 + 인증완료 상태를 서버 메모리에 잠깐 저장해두는 저장소
@Component
public class VerificationCodeRepository {

    private final Map<String, CodeEntry> store = new ConcurrentHashMap<>();
    private final Map<String, LocalDateTime> verifiedStore = new ConcurrentHashMap<>();

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

    // 인증 성공 후 - 회원가입 완료 전까지 "해당 번호 인증 완료" 상태를 30분간 기억해둠
    public void markVerified(String tel) {
        verifiedStore.put(tel, LocalDateTime.now().plusMinutes(30));
    }

    // 회원가입 시 - 이 번호가 인증완료 상태인지 확인
    public boolean isVerified(String tel) {
        LocalDateTime expiredAt = verifiedStore.get(tel);

        if (expiredAt == null) {
            return false;
        }
        if (expiredAt.isBefore(LocalDateTime.now())) {
            verifiedStore.remove(tel);
            return false;
        }
        return true;
    }

    // 회원가입 완료 후 - 인증 상태 초기화 (같은 인증으로 재가입 못 하게 방지)
    public void clearVerified(String tel) {
        verifiedStore.remove(tel);
    }

    private record CodeEntry(String code, LocalDateTime expiredAt) {}
}