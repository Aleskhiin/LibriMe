package org.librime.libribackend.MQHandler.Configuration;

import com.google.cloud.spring.pubsub.core.PubSubTemplate;
import org.librime.libribackend.MQHandler.MessagePublisher;
import org.librime.libribackend.MQHandler.PubSubMessagePublisher;
import org.librime.libribackend.MQHandler.RabbitMQMessagePublisher;
import org.springframework.amqp.rabbit.core.RabbitTemplate;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class MessageConfig {

    @Value("${messaging.provider:rabbitmq}")
    private String provider;

    @Value("${pubsub.topic}")
    private String topicName;

    @Autowired(required = false)
    private RabbitTemplate rabbitTemplate;

    @Autowired(required = false)
    private PubSubTemplate pubSubTemplate;

    @Bean
    public MessagePublisher messagePublisher() {
        if ("pubsub".equalsIgnoreCase(provider)) {
            return new PubSubMessagePublisher(pubSubTemplate, topicName);
        } else {
            return new RabbitMQMessagePublisher(rabbitTemplate);
        }
    }
}
