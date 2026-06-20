package org.librime.libribackend.DB.Repository;

import org.librime.libribackend.DB.Model.Job;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;
import java.util.UUID;

public interface JobRepository extends JpaRepository<Job, Long> {
    Job findByJobID(UUID jobID);

    void deleteAllByJobID(UUID jobID);

    List<Job> searchJobByJobID(UUID jobID);

    List<Job> findAllByUserId(String userId);
}
