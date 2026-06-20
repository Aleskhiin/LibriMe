package org.librime.libribackend.Storage;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;
import org.springframework.core.io.Resource;
import org.springframework.mock.web.MockMultipartFile;

import java.io.IOException;
import java.io.InputStream;
import java.nio.charset.StandardCharsets;
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
        Path storedFile = Path.of(savedPath);
        assertThat(storedFile).exists();
        assertThat(storedFile.getFileName().toString()).isEqualTo(fileName);
        assertThat(storedFile.getParent().getFileName().toString()).isEqualTo(jobId.toString());
        assertThat(Files.readString(storedFile)).isEqualTo(content);
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
    void getInputStream_ShouldReturnValidStream() throws IOException {
        // Given
        UUID jobId = UUID.randomUUID();
        String fileName = "stream-test.txt";
        String content = "Streaming data";
        MockMultipartFile mockFile = new MockMultipartFile("file", fileName, "text/plain", content.getBytes());
        String savedPath = storageService.storeFile(mockFile, jobId);

        // When
        try (InputStream inputStream = storageService.getInputStream(savedPath)) {
            // Then
            assertThat(inputStream).isNotNull();
            String result = new String(inputStream.readAllBytes(), StandardCharsets.UTF_8);
            assertThat(result).isEqualTo(content);
        }
    }
}
