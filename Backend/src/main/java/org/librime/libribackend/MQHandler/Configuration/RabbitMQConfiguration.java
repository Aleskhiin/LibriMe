package org.librime.libribackend.MQHandler.Configuration;

import org.springframework.amqp.core.Binding;
import org.springframework.amqp.core.BindingBuilder;
import org.springframework.amqp.core.Exchange;
import org.springframework.amqp.core.Queue;
import org.springframework.amqp.core.DirectExchange;
import org.springframework.amqp.support.converter.Jackson2JsonMessageConverter;
import org.springframework.amqp.support.converter.MessageConverter;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class RabbitMQConfiguration {
    public static final String NEWQUEUE_NAME = "newjob.queue";
    
    public static final String EXCHANGE_NAME = "job.exchange";

    public static final String NEWROUTING_KEY = "newjob.key";
    


    @Bean
    public Queue newJobQueue() {
        return new Queue(NEWQUEUE_NAME, false);
    }

    @Bean
    public Exchange exchange() {
        return new DirectExchange(EXCHANGE_NAME);
    }

    @Bean
    public MessageConverter jsonMessageConverter() {
        return new Jackson2JsonMessageConverter();
    }

    @Bean
    public Binding newBinding(@Qualifier("newJobQueue") Queue queue, Exchange exchange) {
        return BindingBuilder
                .bind(queue)
                .to(exchange)
                .with(NEWROUTING_KEY).noargs();
    }
}
