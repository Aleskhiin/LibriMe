package org.librime.libribackend.MQHandler;

import org.librime.libribackend.MQHandler.Configuration.RabbitMQConfiguration;
import org.librime.libribackend.MQHandler.MessageRecords.JobMessage;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.amqp.rabbit.core.RabbitTemplate;

public class RabbitMQMessagePublisher implements MessagePublisher {

    private final RabbitTemplate rabbitTemplate;
    private static final Logger log = LoggerFactory.getLogger(RabbitMQMessagePublisher.class);

    public RabbitMQMessagePublisher(RabbitTemplate rabbitTemplate) {
        this.rabbitTemplate = rabbitTemplate;
    }

    @Override
    public void sendMessage(JobMessage message) {
        rabbitTemplate.convertAndSend(
                RabbitMQConfiguration.EXCHANGE_NAME,
                RabbitMQConfiguration.NEWROUTING_KEY,
                message
        );
        log.info("Sent RabbitMQ message: " + message);
    }
}
