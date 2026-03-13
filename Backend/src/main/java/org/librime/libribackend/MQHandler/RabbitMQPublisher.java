package org.librime.libribackend.MQHandler;

import org.librime.libribackend.MQHandler.Configuration.RabbitMQConfiguration;
import org.librime.libribackend.MQHandler.MessageRecords.JobMessage;
import org.librime.libribackend.restservice.Controller.JobController;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.amqp.rabbit.core.RabbitTemplate;
import org.springframework.stereotype.Service;

@Service
public class RabbitMQPublisher {

    private final RabbitTemplate rabbitTemplate;
    private static final Logger log = LoggerFactory.getLogger(RabbitMQPublisher.class);

    public RabbitMQPublisher(RabbitTemplate rabbitTemplate) {
        this.rabbitTemplate = rabbitTemplate;
    }

    public void sendMessage(JobMessage message) {
        rabbitTemplate.convertAndSend(
                RabbitMQConfiguration.EXCHANGE_NAME,
                RabbitMQConfiguration.NEWROUTING_KEY,
                message
        );
        log.info("Sent message: " + message);
    }
}
