package org.librime.libribackend.Storage;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.core.io.Resource;
import org.springframework.core.io.UrlResource;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.io.InputStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.UUID;

public class LocalStorageService implements StorageService {

    private static final Logger log = LoggerFactory.getLogger(LocalStorageService.class);
    private final String localPath;

    public LocalStorageService(String localPath) {
        this.localPath = localPath;
    }

    @Override
    public String storeFile(MultipartFile multipartFile, UUID jobId) {
        String fileName = multipartFile.getOriginalFilename();
        Path jobDirectory = Paths.get(localPath, jobId.toString());
        Path filePath = jobDirectory.resolve(fileName);

        try {
            Files.createDirectories(jobDirectory);
            multipartFile.transferTo(filePath);
            log.info("File {} stored successfully at {}", fileName, filePath);
            return filePath.toString();
        } catch (IOException e) {
            log.error("Failed to store file {}: {}", fileName, e.getMessage());
            throw new RuntimeException("Could not store file", e);
        }
    }

    @Override
    public InputStream getInputStream(String filePath) {
        try {
            return Files.newInputStream(Paths.get(filePath));
        } catch (IOException e) {
            throw new RuntimeException("Could not read file stream", e);
        }
    }

    @Override
    public Resource getResource(String filePath) {
        try {
            return new UrlResource(Paths.get(filePath).toUri());
        } catch (Exception e) {
            throw new RuntimeException("Could not read file", e);
        }
    }
}
