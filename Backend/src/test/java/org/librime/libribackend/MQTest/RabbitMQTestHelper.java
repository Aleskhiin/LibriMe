package org.librime.libribackend.MQTest;

import org.librime.libribackend.MQHandler.Configuration.RabbitMQConfiguration;
import org.librime.libribackend.MQHandler.MessageRecords.JobMessage;
import org.librime.libribackend.restservice.Controller.JobController;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.amqp.rabbit.annotation.RabbitListener;
import org.springframework.amqp.rabbit.core.RabbitTemplate;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;

import java.util.concurrent.BlockingQueue;
import java.util.concurrent.LinkedBlockingQueue;

@Component
public class RabbitMQTestHelper {

    @Autowired
    private RabbitTemplate rabbitTemplate;

    private static final Logger log = LoggerFactory.getLogger(RabbitMQTestHelper.class);

    private final BlockingQueue<JobMessage> messages = new LinkedBlockingQueue<>();

    @RabbitListener(queues = RabbitMQConfiguration.NEWQUEUE_NAME)
    public void receiveMessage(JobMessage message) {
        messages.add(message);
    }

    public JobMessage takeMessage() throws InterruptedException {
        return messages.take();
    }

    public void purgeQueue(){
        rabbitTemplate.execute(channel -> {
            channel.queuePurge(RabbitMQConfiguration.NEWQUEUE_NAME);
            return null;
        });
    }

    public void sendDoneMessage(JobMessage message) {
        rabbitTemplate.convertAndSend(
                RabbitMQConfiguration.EXCHANGE_NAME,
                RabbitMQConfiguration.DONEROUTING_KEY,
                message
        );
        log.info("Sent done message to queue");
    }
}

