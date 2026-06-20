package org.librime.libribackend.DB.Model;

import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import org.librime.libribackend.Types.LanguageType;
import org.librime.libribackend.Types.SplittingType;
import org.librime.libribackend.Types.StatusType;
import org.librime.libribackend.Types.VoiceType;

import java.util.Date;
import java.util.UUID;

@Entity
@Table(name = "jobs")
public class Job {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    private UUID jobID;
    private String OutputFilePath;
    private String InputFilePath;
    private VoiceType voiceID;
    private SplittingType splittingID;
    private LanguageType InputLanguageID;
    private LanguageType OutputLanguageID;
    private StatusType status;
    private int progress;
    private Date timecreated;
    private String userId;

    public Job() {
        // Default constructor
    }

    public Job(UUID jobID,
               String inputFilePath,
               VoiceType voiceID,
               SplittingType splittingType,
               LanguageType inputLanguage,
               LanguageType outputLanguage,
               StatusType status)
    {
        this.jobID = jobID;
        this.OutputFilePath = "";
        this.InputFilePath = inputFilePath;
        this.voiceID = voiceID;
        this.splittingID = splittingType;
        this.InputLanguageID = inputLanguage;
        this.OutputLanguageID = outputLanguage;
        this.status = status;
        this.progress = 0;
        this.timecreated = new Date();
        this.userId = "";
    }

    // Getters
    public Long getId() {
        return id;
    }

    public UUID getJobID() {
        return jobID;
    }

    public String getOutputFilePath() {
        return OutputFilePath;
    }

    public String getInputFilePath() {
        return InputFilePath;
    }

    public VoiceType getVoiceID () {
        return voiceID;
    }

    public SplittingType getSplittingID() {
        return splittingID;
    }

    public LanguageType getInputLanguageID() {
        return InputLanguageID;
    }

    public LanguageType getOutputLanguageID() {
        return OutputLanguageID;
    }

    public StatusType getStatus() {
        return status;
    }

    public int getProgress() {
        return progress;
    }

    public Date getTimecreated() {
        return timecreated;
    }

    public String getUserId() {
        return userId;
    }

    // Setters
    public void setId(Long id) {
        this.id = id;
    }

    public void setOutputFilePath(String fileName) {
        this.OutputFilePath = fileName;
    }

    public void setInputFilePath(String filePath) {
        this.InputFilePath = filePath;
    }

    public void setVoiceID(VoiceType voiceID) {
        this.voiceID = voiceID;
    }

    public void setSplittingID(SplittingType splittingID) {
        this.splittingID = splittingID;
    }

    public void setInputLanguageID(LanguageType languageID) {
        this.InputLanguageID = languageID;
    }

    public void setOutputLanguageID(LanguageType languageID) {
        this.OutputLanguageID = languageID;
    }

    public void setStatus(StatusType status) {
        this.status = status;
    }

    public void setProgress(int progress) {
        this.progress = progress;
    }

    public void setTimecreated(Date timecreated) {
        this.timecreated = timecreated;
    }

    public void setUserId(String userId) {
        this.userId = userId;
    }
}
