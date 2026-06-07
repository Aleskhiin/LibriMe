package org.librime.libribackend.MQHandler.Configuration;

import org.librime.libribackend.MQHandler.MessagePublisher;
import org.librime.libribackend.MQHandler.PubSubMessagePublisher;
import org.librime.libribackend.MQHandler.RabbitMQMessagePublisher;
import org.springframework.amqp.rabbit.core.RabbitTemplate;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class MessageConfig {

    @Value("${messaging.provider:rabbitmq}")
    private String provider;

    @Bean
    public MessagePublisher messagePublisher(RabbitTemplate rabbitTemplate) {
        if ("pubsub".equalsIgnoreCase(provider)) {
            return new PubSubMessagePublisher();
        } else {
            return new RabbitMQMessagePublisher(rabbitTemplate);
        }
    }
}
