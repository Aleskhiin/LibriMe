package org.librime.libribackend.restservice.Controller;

import org.librime.libribackend.DB.JobService;
import org.librime.libribackend.DB.Model.Job;
import org.librime.libribackend.MQHandler.MessageRecords.NewJobMessage;
import org.librime.libribackend.MQHandler.MessagePublisher;
import org.librime.libribackend.Storage.StorageService;
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
import org.springframework.http.MediaType;
import org.springframework.security.core.context.SecurityContextHolder;

import java.net.MalformedURLException;
import java.util.List;
import java.util.UUID;
import java.util.stream.Collectors;

@RestController
@RequestMapping("/")
public class JobController {

    private final JobService jobService;
    private final MessagePublisher messagePublisher;
    private final StorageService storageService;

    private static final Logger log = LoggerFactory.getLogger(JobController.class);

    @Autowired
    public JobController(JobService jobService, MessagePublisher messagePublisher, StorageService storageService) {
        this.jobService = jobService;
        this.messagePublisher = messagePublisher;
        this.storageService = storageService;
    }

    private String getCurrentUserId() {
        return (String) SecurityContextHolder.getContext().getAuthentication().getPrincipal();
    }

    @GetMapping("/jobs")
    public ResponseEntity<List<JobRecord>> getAllJobs() {
        String userId = getCurrentUserId();
        log.info("Received request for all jobs for user: {}", userId);
        List<Job> jobs = jobService.getJobsByUserId(userId);
        List<JobRecord> jobRecords = jobs.stream()
                .map(job -> new StatusJobRecord(job.getJobID(), job.getStatus(), job.getProgress(), "/jobs/"+job.getJobID()+"/result", ""))
                .collect(Collectors.toList());
        return new ResponseEntity<>(jobRecords, HttpStatus.OK);
    }

    @PostMapping("/jobs")
    public ResponseEntity<JobRecord> newJob(@RequestParam("file") MultipartFile multipartFile,
                            @RequestParam("fileLanguage") LanguageType fileLanguage,
                            @RequestParam("translationLanguage") LanguageType translationLanguage,
                            @RequestParam("voiceID") VoiceType voiceType,
                            @RequestParam("splittingID") SplittingType splittingType ){
        UUID uuid = UUID.randomUUID();
        String userId = getCurrentUserId();
        String fileName = multipartFile.getOriginalFilename();

        log.info("Received file: {} and input language type: {} and output language type: {} and voice type: {}. creating job {} for user {}",
                fileName, fileLanguage, translationLanguage, voiceType, uuid, userId);

        String filePath = storageService.storeFile(multipartFile, uuid);

        log.info("file: {} transfered to {} ",fileName, filePath);
        Job job = new Job(uuid, filePath, voiceType, splittingType, fileLanguage, translationLanguage, StatusType.QUEUED);
        job.setUserId(userId);
        jobService.createJob(job);
        messagePublisher.sendMessage(new NewJobMessage(uuid, fileLanguage, translationLanguage, voiceType, filePath, splittingType));

        return new ResponseEntity<>(new NewJobRecord(uuid, StatusType.QUEUED, "queued file:"+multipartFile.getOriginalFilename(), "/jobs/"+uuid), HttpStatus.ACCEPTED);
    }

    @GetMapping("/jobs/{jobID}")
    public ResponseEntity<JobRecord>  updateJob(@PathVariable UUID jobID){
        log.info("Received status request for job ID: {}", jobID);
        Job job = jobService.getJobByJobId(jobID);
        if (job == null) {
            return new ResponseEntity<>(HttpStatus.NOT_FOUND);
        }
        if (!job.getUserId().equals(getCurrentUserId())) {
            return new ResponseEntity<>(HttpStatus.FORBIDDEN);
        }
        return new ResponseEntity<>(new StatusJobRecord(job.getJobID(), job.getStatus(), job.getProgress(), "/jobs/"+jobID+"/result", ""), HttpStatus.OK);
    }

    @PutMapping("/jobs/{jobID}")
    public ResponseEntity<JobRecord>  statusJob(@PathVariable UUID jobID,
                                                @RequestParam("status") StatusType status,
                                                @RequestParam("progress") int progress,
                                                @RequestParam("outputFilePath") String OutputFilePath
    ) {
        log.info("Received update request for job ID: {}", jobID);

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
        if (job == null) {
            return new ResponseEntity<>(HttpStatus.NOT_FOUND);
        }
        if (!job.getUserId().equals(getCurrentUserId())) {
            return new ResponseEntity<>(HttpStatus.FORBIDDEN);
        }

        String signedUrl = storageService.getDownloadUrl(job.getOutputFilePath());
        if (signedUrl != null) {
            log.info("Redirecting user to signed URL for job ID: {}", jobID);
            return ResponseEntity.status(HttpStatus.FOUND)
                    .header(HttpHeaders.LOCATION, signedUrl)
                    .build();
        }

        Resource resource = storageService.getResource(job.getOutputFilePath());
        return ResponseEntity.ok()
                .contentType(MediaType.parseMediaType("audio/mpeg"))
                .header(HttpHeaders.CONTENT_DISPOSITION, "attachment; filename=\"" + resource.getFilename() + "\"")
                .body(resource);
    }
}
