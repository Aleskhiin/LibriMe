package org.librime.libribackend.Storage;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class StorageConfig {

    @Value("${storage.provider}")
    private String provider;

    @Value("${storage.local-path}")
    private String localPath;

    @Bean
    public StorageService storageService() {
        if ("gcs".equalsIgnoreCase(provider)) {
            return new GcsStorageService();
        } else {
            return new LocalStorageService(localPath);
        }
    }
}
