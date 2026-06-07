package org.librime.libribackend.MQHandler;

import com.google.cloud.spring.pubsub.core.PubSubTemplate;
import org.junit.jupiter.api.Test;
import org.librime.libribackend.MQHandler.MessageRecords.NewJobMessage;
import org.librime.libribackend.Types.LanguageType;
import org.librime.libribackend.Types.SplittingType;
import org.librime.libribackend.Types.VoiceType;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.beans.factory.annotation.Autowired;
import java.util.concurrent.CompletableFuture;

import java.util.UUID;

import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

@SpringBootTest(properties = {
    "spring.cloud.gcp.pubsub.enabled=false",
    "spring.cloud.gcp.sql.enabled=false"
})
class PubSubMessagePublisherTest {

    @Configuration
    static class TestConfig {
        @Bean
        public PubSubMessagePublisher pubSubMessagePublisher(PubSubTemplate pubSubTemplate) {
            return new PubSubMessagePublisher(pubSubTemplate, "test-topic");
        }
    }

    @MockBean
    private PubSubTemplate pubSubTemplate;

    @Autowired
    private PubSubMessagePublisher publisher;

    @Test
    void testSendMessageSuccessfully() {
        NewJobMessage message = new NewJobMessage(UUID.randomUUID(), LanguageType.en_US, LanguageType.en_US, VoiceType.male_v1, "path", SplittingType.DOCUMENT);
        when(pubSubTemplate.publish(any(), any())).thenReturn(CompletableFuture.completedFuture("message-id"));
        
        publisher.sendMessage(message);
        verify(pubSubTemplate).publish(eq("test-topic"), eq(message));
    }
}
