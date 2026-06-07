package org.librime.libribackend.Storage;

import org.springframework.core.io.Resource;
import org.springframework.web.multipart.MultipartFile;
import java.io.File;
import java.util.UUID;

public interface StorageService {
    String storeFile(MultipartFile file, UUID jobId);
    File getFile(String filePath);
    Resource getResource(String filePath);
}
