package org.librime.libribackend.Storage;

import com.google.cloud.storage.BlobId;
import com.google.cloud.storage.BlobInfo;
import com.google.cloud.storage.Storage;
import com.google.cloud.spring.storage.GoogleStorageResource;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.core.io.Resource;
import org.springframework.web.multipart.MultipartFile;

import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.util.UUID;

public class GcsStorageService implements StorageService {

    private static final Logger log = LoggerFactory.getLogger(GcsStorageService.class);
    private final Storage storage;
    private final String bucketName;

    public GcsStorageService(Storage storage, String bucketName) {
        this.storage = storage;
        this.bucketName = bucketName;
    }

    @Override
    public String storeFile(MultipartFile file, UUID jobId) {
        String fileName = jobId.toString() + "/" + file.getOriginalFilename();
        BlobId blobId = BlobId.of(bucketName, fileName);
        BlobInfo blobInfo = BlobInfo.newBuilder(blobId).setContentType(file.getContentType()).build();

        try {
            storage.create(blobInfo, file.getBytes());
            log.info("File {} stored successfully in bucket {}", fileName, bucketName);
            return fileName; // Return the blob name as the "path"
        } catch (IOException e) {
            log.error("Failed to store file to GCS: {}", e.getMessage());
            throw new RuntimeException("Could not store file to GCS", e);
        }
    }

    @Override
    public File getFile(String filePath) {
        try {
            // For GCS, we download to a temporary file because the internal logic expects a File
            File tempFile = File.createTempFile("gcs-download-", ".tmp");
            storage.get(BlobId.of(bucketName, filePath)).downloadTo(tempFile.toPath());
            return tempFile;
        } catch (IOException e) {
            throw new RuntimeException("Failed to download file from GCS", e);
        }
    }

    @Override
    public Resource getResource(String filePath) {
        return new GoogleStorageResource(storage, "gs://" + bucketName + "/" + filePath);
    }
}
