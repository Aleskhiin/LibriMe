package org.librime.libribackend.restservice.Controller;

import org.librime.libribackend.DB.JobService;
import org.librime.libribackend.DB.Model.Job;
import org.librime.libribackend.Exception.ResourceNotFoundException;
import org.librime.libribackend.Exception.UnauthorizedAccessException;
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
import jakarta.servlet.http.HttpServletResponse;
import org.springframework.http.ResponseCookie;
import org.librime.libribackend.Security.JwtUtil;

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
    private final JwtUtil jwtUtil;

    private static final Logger log = LoggerFactory.getLogger(JobController.class);

    @Autowired
    public JobController(JobService jobService, MessagePublisher messagePublisher, StorageService storageService, JwtUtil jwtUtil) {
        this.jobService = jobService;
        this.messagePublisher = messagePublisher;
        this.storageService = storageService;
        this.jwtUtil = jwtUtil;
    }

    private String getCurrentUserId() {
        return (String) SecurityContextHolder.getContext().getAuthentication().getPrincipal();
    }

    private Job getJobAndValidateOwnership(UUID jobID) {
        Job job = jobService.getJobByJobId(jobID);
        if (job == null) {
            throw new ResourceNotFoundException("Job with ID " + jobID + " not found");
        }
        if (!job.getUserId().equals(getCurrentUserId())) {
            throw new UnauthorizedAccessException("You do not have permission to access this job");
        }
        return job;
    }

    private String getJobRecordDownloadUrl(Job job) {
        if (job.getStatus() == StatusType.COMPLETED && job.getOutputFilePath() != null) {
            try {
                String signedUrl = storageService.getDownloadUrl(job.getOutputFilePath());
                if (signedUrl != null) {
                    return signedUrl;
                }
            } catch (Exception e) {
                log.error("Failed to generate signed download URL for job {}: {}", job.getJobID(), e.getMessage());
            }
        }
        return "/jobs/" + job.getJobID() + "/result";
    }

    private String getFileNameFromPath(String path) {
        if (path == null) {
            return "";
        }
        int lastSlash = Math.max(path.lastIndexOf('/'), path.lastIndexOf('\\'));
        if (lastSlash >= 0) {
            return path.substring(lastSlash + 1);
        }
        return path;
    }

    private StatusJobRecord mapToStatusJobRecord(Job job) {
        return new StatusJobRecord(
                job.getJobID(),
                job.getStatus(),
                job.getProgress(),
                getJobRecordDownloadUrl(job),
                "",
                getFileNameFromPath(job.getInputFilePath()),
                job.getInputLanguageID(),
                job.getOutputLanguageID(),
                job.getVoiceID(),
                job.getSplittingID()
        );
    }

    @GetMapping("/jobs")
    public List<JobRecord> getAllJobs() {
        String userId = getCurrentUserId();
        log.info("Received request for all jobs for user: {}", userId);
        List<Job> jobs = jobService.getJobsByUserId(userId);
        return jobs.stream()
                .map(this::mapToStatusJobRecord)
                .collect(Collectors.toList());
    }

    @PostMapping("/jobs")
    @ResponseStatus(HttpStatus.ACCEPTED)
    public JobRecord createJob(@RequestParam("file") MultipartFile multipartFile,
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

        log.info("file: {} transferred to {} ", fileName, filePath);
        Job job = new Job(uuid, filePath, voiceType, splittingType, fileLanguage, translationLanguage, StatusType.QUEUED);
        job.setUserId(userId);
        jobService.createJob(job);
        messagePublisher.sendMessage(new NewJobMessage(uuid, fileLanguage, translationLanguage, voiceType, filePath, splittingType));

        return new NewJobRecord(uuid, StatusType.QUEUED, "queued file:"+multipartFile.getOriginalFilename(), "/jobs/"+uuid);
    }

    @GetMapping("/jobs/{jobID}")
    public JobRecord getJobStatus(@PathVariable UUID jobID){
        log.info("Received status request for job ID: {}", jobID);
        Job job = getJobAndValidateOwnership(jobID);
        return mapToStatusJobRecord(job);
    }

    @PutMapping("/jobs/{jobID}")
    public JobRecord updateJobStatus(@PathVariable UUID jobID,
                                     @RequestParam("status") StatusType status,
                                     @RequestParam("progress") int progress,
                                     @RequestParam("outputFilePath") String outputFilePath
    ) {
        log.info("Received update request for job ID: {}", jobID);

        Job job = jobService.getJobByJobId(jobID);
        if (job == null) {
            throw new ResourceNotFoundException("Job with ID " + jobID + " not found");
        }

        job.setStatus(status);
        job.setProgress(progress);
        job.setOutputFilePath(outputFilePath);

        jobService.updateJob(job);

        return mapToStatusJobRecord(job);
    }

    @GetMapping("/jobs/{jobID}/result")
    public ResponseEntity<Resource> getJobResult(@PathVariable UUID jobID) throws MalformedURLException {
        log.info("Received result request for job ID: {}", jobID);
        Job job = getJobAndValidateOwnership(jobID);

        // Try to get a signed URL first (for GCS)
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

    @PostMapping("/auth/logout")
    public ResponseEntity<Void> logout(HttpServletResponse response) {
        String newLocalJwt = jwtUtil.generateToken(UUID.randomUUID().toString());
        ResponseCookie cookie = ResponseCookie.from("libriME_jwt", newLocalJwt)
                .httpOnly(true)
                .secure(true)
                .path("/")
                .maxAge(60 * 60 * 24 * 30) // 30 days
                .sameSite("None")
                .build();
        response.addHeader(HttpHeaders.SET_COOKIE, cookie.toString());
        return ResponseEntity.ok().build();
    }
}
