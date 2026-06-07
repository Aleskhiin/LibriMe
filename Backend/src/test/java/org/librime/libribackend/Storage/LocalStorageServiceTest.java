package org.librime.libribackend.Storage;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;
import org.springframework.core.io.Resource;
import org.springframework.mock.web.MockMultipartFile;

import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.UUID;

import static org.assertj.core.api.Assertions.assertThat;

class LocalStorageServiceTest {

    @TempDir
    Path tempDir;

    private LocalStorageService storageService;

    @BeforeEach
    void setUp() {
        storageService = new LocalStorageService(tempDir.toString());
    }

    @Test
    void storeFile_ShouldSaveFileToCorrectDirectory() throws IOException {
        // Given
        UUID jobId = UUID.randomUUID();
        String fileName = "test.txt";
        String content = "Hello, Storage!";
        MockMultipartFile mockFile = new MockMultipartFile("file", fileName, "text/plain", content.getBytes());

        // When
        String savedPath = storageService.storeFile(mockFile, jobId);

        // Then
        File storedFile = new File(savedPath);
        assertThat(storedFile).exists();
        assertThat(storedFile.getName()).isEqualTo(fileName);
        assertThat(storedFile.getParentFile().getName()).isEqualTo(jobId.toString());
        assertThat(Files.readString(Path.of(savedPath))).isEqualTo(content);
    }

    @Test
    void getResource_ShouldReturnValidResource() throws IOException {
        // Given
        UUID jobId = UUID.randomUUID();
        String fileName = "resource-test.txt";
        MockMultipartFile mockFile = new MockMultipartFile("file", fileName, "text/plain", "content".getBytes());
        String savedPath = storageService.storeFile(mockFile, jobId);

        // When
        Resource resource = storageService.getResource(savedPath);

        // Then
        assertThat(resource).isNotNull();
        assertThat(resource.exists()).isTrue();
        assertThat(resource.getFilename()).isEqualTo(fileName);
    }

    @Test
    void getFile_ShouldReturnFileObject() {
        // Given
        String path = "/some/path/to/file.txt";

        // When
        File file = storageService.getFile(path);

        // Then
        assertThat(file).isNotNull();
        assertThat(file.getPath()).isEqualTo(path);
    }
}
