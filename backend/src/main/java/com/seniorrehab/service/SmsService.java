package com.seniorrehab.service;

import net.nurigo.sdk.NurigoApp;
import net.nurigo.sdk.message.model.Message;
import net.nurigo.sdk.message.request.SingleMessageSendingRequest;
import net.nurigo.sdk.message.service.DefaultMessageService;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

@Service
public class SmsService {

    private final DefaultMessageService messageService;
    private final String sender;
    private final boolean enabled; // 추가: 실제 발송 ON/OFF

    public SmsService(
            @Value("${solapi.api-key}") String apiKey,
            @Value("${solapi.api-secret}") String apiSecret,
            @Value("${solapi.sender}") String sender,
            @Value("${sms.enabled:false}") boolean enabled) { // 추가: 설정 없으면 false
        this.messageService = NurigoApp.INSTANCE.initialize(apiKey, apiSecret, "https://api.solapi.com");
        this.sender = sender;
        this.enabled = enabled; // 추가
    }

    // SMS 발송
    public void sendSms(String to, String text) {
        // 추가: 꺼져 있으면 실제 발송 없이 콘솔에만 출력
        if (!enabled) {
            System.out.println("[SMS 꺼짐] " + to + " / " + text);
            return;
        }

        Message message = new Message();
        message.setFrom(sender);
        message.setTo(to);
        message.setText(text);
        messageService.sendOne(new SingleMessageSendingRequest(message));
    }
}