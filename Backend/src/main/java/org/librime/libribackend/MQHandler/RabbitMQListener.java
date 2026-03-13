package org.librime.libribackend.MQHandler;

import org.librime.libribackend.DBAccess.JobService;
import org.librime.libribackend.DBAccess.Model.Job;
import org.librime.libribackend.MQHandler.Configuration.RabbitMQConfiguration;
import org.librime.libribackend.MQHandler.MessageRecords.JobMessage;
import org.librime.libribackend.MQHandler.MessageRecords.RunningJobMessage;
import org.librime.libribackend.restservice.Controller.JobController;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.amqp.rabbit.annotation.RabbitListener;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

@Service
public class RabbitMQListener {

    @Autowired
    private JobService jobService;

    private static final Logger log = LoggerFactory.getLogger(RabbitMQListener.class);

    @RabbitListener(queues = RabbitMQConfiguration.DONEQUEUE_NAME)
    public void receiveMessage(JobMessage message) {
        acceptAndProcess(message);
    }

    private void acceptAndProcess(JobMessage message) {
        if(message instanceof RunningJobMessage){
            updateJobInDB((RunningJobMessage) message);
        }else{
            log.info("Uknown JobMessage type: " + message.getClass().getName()+" received");
        }
    }

    private void updateJobInDB(RunningJobMessage message) {
        jobService.updateJobStatus(message.jobID(), message.status());
        jobService.updateJobProgress(message.jobID(), message.progress());
        jobService.updateJobResultPath(message.jobID(), message.resultPath());
        log.info("Job updated in DB");
    }
}
