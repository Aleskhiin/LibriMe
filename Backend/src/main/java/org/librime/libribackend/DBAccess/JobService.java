package org.librime.libribackend.DBAccess;

import org.librime.libribackend.DBAccess.Model.Job;
import org.librime.libribackend.DBAccess.Repository.JobRepository;
import org.librime.libribackend.Types.StatusType;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.UUID;

@Service
public class JobService {
    @Autowired
    private JobRepository jobRepository;

    public List<Job> getAllJobs() {
        return jobRepository.findAll();
    }

    public Job getJobByJobId(UUID jobId) {
        return jobRepository.findByJobID(jobId);
    }

    public boolean hasJobByJobId(UUID jobID) {
        return !jobRepository.searchJobByJobID(jobID).isEmpty();
    }

    public Job createJob(Job job) {
        return jobRepository.save(job);
    }

    public Job updateJobStatus(UUID jobID, StatusType status) {
        Job existingJob = jobRepository.findByJobID(jobID);
        if (existingJob != null) {
            existingJob.setStatus(status);
            return jobRepository.save(existingJob);
        } else {
            return null;
        }
    }

    public Job updateJobProgress(UUID jobID, int progress) {
        Job existingJob = jobRepository.findByJobID(jobID);
        if (existingJob != null) {
            existingJob.setProgress(progress);
            return jobRepository.save(existingJob);
        } else {
            return null;
        }
    }

    public Job updateJobResultPath(UUID jobID, String path) {
        Job existingJob = jobRepository.findByJobID(jobID);
        if (existingJob != null) {
            existingJob.setOutputFilePath(path);
            return jobRepository.save(existingJob);
        } else {
            return null;
        }
    }

    public void deleteJob (UUID jobID) {
        jobRepository.deleteAllByJobID(jobID);
    }

    public void deleteJob (Job job) {
        jobRepository.delete(job);
    }
}
