package com.seniorrehab.model.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;

@Getter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class CheckPhoneResponseDto {
    
    private boolean avilable;   // true : 사용 가능, false : 이미 가입된 번호
}
