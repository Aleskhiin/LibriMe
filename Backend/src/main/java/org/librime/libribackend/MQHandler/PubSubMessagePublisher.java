package org.librime.libribackend.MQHandler;

import org.librime.libribackend.MQHandler.MessageRecords.JobMessage;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class PubSubMessagePublisher implements MessagePublisher {
    
    private static final Logger log = LoggerFactory.getLogger(PubSubMessagePublisher.class);

    @Override
    public void sendMessage(JobMessage message) {
        // TODO: Implement GCP Pub/Sub logic using Spring Cloud GCP
        log.warn("Pub/Sub messaging not implemented yet. Message was: {}", message);
        throw new UnsupportedOperationException("Pub/Sub messaging not implemented yet");
    }
}
