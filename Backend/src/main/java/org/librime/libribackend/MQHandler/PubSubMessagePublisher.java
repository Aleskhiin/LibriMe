package org.librime.libribackend.MQHandler;

import com.google.cloud.spring.pubsub.core.PubSubTemplate;
import org.librime.libribackend.MQHandler.MessageRecords.JobMessage;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;

public class PubSubMessagePublisher implements MessagePublisher {
    
    private static final Logger log = LoggerFactory.getLogger(PubSubMessagePublisher.class);
    private final PubSubTemplate pubSubTemplate;
    private final String topicName;

    public PubSubMessagePublisher(PubSubTemplate pubSubTemplate, String topicName) {
        this.pubSubTemplate = pubSubTemplate;
        this.topicName = topicName;
    }

    @Override
    public void sendMessage(JobMessage message) {
        try {
            pubSubTemplate.publish(topicName, message);
            log.info("Successfully published message to Pub/Sub topic {}: {}", topicName, message);
        } catch (Exception e) {
            log.error("Failed to publish message to Pub/Sub: {}", e.getMessage());
            throw new RuntimeException("Could not publish message to Pub/Sub", e);
        }
    }
}
