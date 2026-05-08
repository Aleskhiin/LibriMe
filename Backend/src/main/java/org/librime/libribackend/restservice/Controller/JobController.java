package org.librime.libribackend.restservice.Controller;

import org.librime.libribackend.DBAccess.JobService;
import org.librime.libribackend.DBAccess.Model.Job;
import org.librime.libribackend.MQHandler.MessageRecords.NewJobMessage;
import org.librime.libribackend.MQHandler.RabbitMQPublisher;
import org.librime.libribackend.Types.LanguageType;
import org.librime.libribackend.Types.SplittingType;
import org.librime.libribackend.Types.StatusType;
import org.librime.libribackend.Types.VoiceType;
import org.librime.libribackend.restservice.Records.JobRecord;
import org.librime.libribackend.restservice.Records.NewJobRecord;
import org.librime.libribackend.restservice.Records.StatusJobRecord;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;
import org.springframework.core.io.Resource;
import org.springframework.core.io.UrlResource;
import org.springframework.http.MediaType;

import java.io.File;
import java.io.IOException;
import java.net.MalformedURLException;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.UUID;

@RestController
@RequestMapping("/")
public class JobController {

    @Autowired
    private JobService jobService;

    @Autowired
    private RabbitMQPublisher rabbitMQPublisher;

    private static final Logger log = LoggerFactory.getLogger(JobController.class);

    JobController(){
    }

    @PostMapping("/jobs")
    public ResponseEntity<JobRecord> newJob(@RequestParam("file") MultipartFile multipartFile,
                            @RequestParam("fileLanguage") LanguageType fileLanguage,
                            @RequestParam("translationLanguage") LanguageType translationLanguage,
                            @RequestParam("voiceID") VoiceType voiceType,
                            @RequestParam("splittingID") SplittingType splittingType ){
        UUID uuid = UUID.randomUUID();
        String fileName = multipartFile.getOriginalFilename();
        String filePath = "/opt/librime/files/"+ uuid + File.separator + fileName;

        log.info("Received file: {} and input language type: {} and output language type: {} and voice type: {}. creating job {}",
                fileName, fileLanguage, translationLanguage, voiceType, uuid);

        try {
            File file = new File(filePath);
            file.getParentFile().mkdirs();
            file.createNewFile();
            multipartFile.transferTo(file.toPath());
        }
        catch(Exception e) {
            log.error(e.getMessage());
        }

        log.info("file: {} transfered to {} ",fileName, filePath);
        jobService.createJob(new Job(uuid, filePath, voiceType, splittingType, fileLanguage, translationLanguage, StatusType.QUEUED));
        rabbitMQPublisher.sendMessage(new NewJobMessage(uuid, fileLanguage, translationLanguage, voiceType, filePath, splittingType));

        return new ResponseEntity<>(new NewJobRecord(uuid, StatusType.QUEUED, "queued file:"+multipartFile.getOriginalFilename(), "/jobs/"+uuid), HttpStatus.ACCEPTED);
    }

    @GetMapping("/jobs/{jobID}")
    public ResponseEntity<JobRecord>  updateJob(@PathVariable UUID jobID){
        log.info("Received update request for job ID: {}", jobID);
        Job job = jobService.getJobByJobId(jobID);
        return new ResponseEntity<>(new StatusJobRecord(job.getJobID(), job.getStatus(), job.getProgress(), "/jobs/"+jobID+"/result", ""), HttpStatus.OK);
    }

    @PutMapping("/jobs/{jobID}")
    public ResponseEntity<JobRecord>  statusJob(@PathVariable UUID jobID,
                                                @RequestParam("status") StatusType status,
                                                @RequestParam("progress") int progress,
                                                @RequestParam("outputFilePath") String OutputFilePath
    ) {
        log.info("Received status request for job ID: {}", jobID);

        Job job = jobService.getJobByJobId(jobID);

        job.setStatus(status);
        job.setProgress(progress);
        job.setOutputFilePath(OutputFilePath);

        jobService.updateJob(job);

        return new ResponseEntity<>(new StatusJobRecord(job.getJobID(), job.getStatus(), job.getProgress(), "/jobs/"+jobID+"/result", ""), HttpStatus.OK);
    }

    @GetMapping("/jobs/{jobID}/result")
    public ResponseEntity<Resource> result(@PathVariable UUID jobID) throws MalformedURLException {
        log.info("Received result request for job ID: {}", jobID);
        Job job = jobService.getJobByJobId(jobID);
        Path path = Paths.get(job.getOutputFilePath());
        // Load the resource
        Resource resource = new UrlResource(path.toUri());

        return ResponseEntity.ok()
                .contentType(MediaType.parseMediaType("audio/mpeg"))
                .header(HttpHeaders.CONTENT_DISPOSITION, "attachment; filename=\"" + resource.getFilename() + "\"")
                .body(resource);
    }
}
