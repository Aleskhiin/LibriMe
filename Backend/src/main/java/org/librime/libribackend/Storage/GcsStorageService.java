package org.librime.libribackend.Storage;

import org.springframework.core.io.Resource;
import org.springframework.web.multipart.MultipartFile;
import java.io.File;
import java.util.UUID;

public class GcsStorageService implements StorageService {
    @Override
    public String storeFile(MultipartFile file, UUID jobId) {
        // TODO: Implement GCS storage logic using Google Cloud SDK
        throw new UnsupportedOperationException("GCS Storage not implemented yet");
    }

    @Override
    public File getFile(String filePath) {
        // TODO: Implement GCS file retrieval logic
        throw new UnsupportedOperationException("GCS Storage not implemented yet");
    }

    @Override
    public Resource getResource(String filePath) {
        // TODO: Implement GCS resource retrieval logic
        throw new UnsupportedOperationException("GCS Storage not implemented yet");
    }
}
