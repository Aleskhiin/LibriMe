package org.librime.libribackend.Storage;

import com.google.cloud.storage.Storage;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class StorageConfig {

    @Value("${storage.provider}")
    private String provider;

    @Value("${storage.local-path}")
    private String localPath;

    @Value("${gcp.storage.bucket}")
    private String bucketName;

    @Autowired(required = false)
    private Storage storage;

    @Bean
    public StorageService storageService() {
        if ("gcs".equalsIgnoreCase(provider)) {
            return new GcsStorageService(storage, bucketName);
        } else {
            return new LocalStorageService(localPath);
        }
    }
}
