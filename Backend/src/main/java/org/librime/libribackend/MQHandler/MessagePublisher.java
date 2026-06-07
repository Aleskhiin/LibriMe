package org.librime.libribackend.MQHandler;

import org.librime.libribackend.MQHandler.MessageRecords.JobMessage;

public interface MessagePublisher {
    void sendMessage(JobMessage message);
}
