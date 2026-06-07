package org.librime.libribackend;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.librime.libribackend.DB.JobService;
import org.librime.libribackend.DB.Model.Job;
import org.librime.libribackend.MQHandler.MessageRecords.NewJobMessage;
import org.librime.libribackend.MQTest.RabbitMQTestHelper;
import org.librime.libribackend.Types.LanguageType;
import org.librime.libribackend.Types.SplittingType;
import org.librime.libribackend.Types.StatusType;
import org.librime.libribackend.Types.VoiceType;
import org.librime.libribackend.restservice.Records.NewJobRecord;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.core.io.ClassPathResource;
import org.springframework.http.client.MultipartBodyBuilder;
import org.springframework.http.ResponseCookie;
import org.springframework.test.web.reactive.server.WebTestClient;
import org.springframework.test.web.reactive.server.FluxExchangeResult;
import org.springframework.web.reactive.function.BodyInserters;

import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.nio.file.StandardCopyOption;
import java.util.UUID;

import static org.assertj.core.api.Assertions.assertThat;

@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
class LibriMeBackendIntegrationTests {

    @Autowired
    private WebTestClient webClient;

    @Autowired
    private JobService jobService;

    @Autowired
    private RabbitMQTestHelper rabbitMQhelper;

    private final String dummyUUID = "00000000-0000-0000-0000-000000000000";

    @BeforeEach
    void beforeEach() throws IOException, InterruptedException {
        rabbitMQhelper.purgeQueue();
    }

    private ResponseCookie getSessionCookie() {
        return webClient.get().uri("/jobs")
                .exchange()
                .returnResult(Object.class)
                .getResponseCookies()
                .getFirst("libriME_jwt");
    }

    void createJobForUser(UUID jobId, String userId) throws IOException {
        String filePath = "/opt/librime/files/test/";
        File file = new File(filePath);
        file.mkdirs();

        Job job = new Job(jobId, filePath+"test.pdf", VoiceType.male_v1, SplittingType.DOCUMENT, LanguageType.en_US, LanguageType.en_US, StatusType.QUEUED);
        job.setUserId(userId);
        jobService.createJob(job);
        
        Files.copy(Paths.get(System.getProperty("user.dir"),"src/test/resources/test.mp3"), Paths.get(filePath, "test.mp3"), StandardCopyOption.REPLACE_EXISTING);
        Files.copy(Paths.get(System.getProperty("user.dir"),"src/test/resources/test.pdf"), Paths.get(filePath, "test.pdf"), StandardCopyOption.REPLACE_EXISTING);
        jobService.updateJobResultPath(jobId, filePath+"test.mp3");
    }

    @Test
    void UploadNewFileTest() throws InterruptedException {
        MultipartBodyBuilder builder = new MultipartBodyBuilder();
        builder.part("file", new ClassPathResource("test.pdf"));
        builder.part("fileLanguage", "en_US");
        builder.part("translationLanguage", "en_US");
        builder.part("voiceID", "male_v1");
        builder.part("splittingID", "DOCUMENT");

        webClient.post().uri("/jobs")
                .body(BodyInserters.fromMultipartData(builder.build()))
                .exchange()
                .expectStatus().isAccepted()
                .expectBody(NewJobRecord.class);

        NewJobMessage received = (NewJobMessage) rabbitMQhelper.takeMessage();

        assertThat(received).isEqualTo(new NewJobMessage(
                received.jobID(),
                LanguageType.en_US,
                LanguageType.en_US,
                VoiceType.male_v1,
                "/opt/librime/files/"+ received.jobID() + File.separator + "test.pdf",
                SplittingType.DOCUMENT));
    }

    @Test
    void GetJobStatusTest() throws IOException {
        ResponseCookie cookie = getSessionCookie();

        MultipartBodyBuilder builder = new MultipartBodyBuilder();
        builder.part("file", new ClassPathResource("test.pdf"));
        builder.part("fileLanguage", "en_US");
        builder.part("translationLanguage", "en_US");
        builder.part("voiceID", "male_v1");
        builder.part("splittingID", "DOCUMENT");

        NewJobRecord newJob = webClient.post().uri("/jobs")
                .cookie(cookie.getName(), cookie.getValue())
                .body(BodyInserters.fromMultipartData(builder.build()))
                .exchange()
                .expectStatus().isAccepted()
                .expectBody(NewJobRecord.class)
                .returnResult().getResponseBody();

        assertThat(newJob).isNotNull();

        webClient.get().uri("/jobs/"+newJob.jobID())
                .cookie(cookie.getName(), cookie.getValue())
                .exchange()
                .expectStatus()
                .isOk();
    }

    @Test
    void  GetJobResultTest() throws IOException {
        ResponseCookie cookie = getSessionCookie();

        MultipartBodyBuilder builder = new MultipartBodyBuilder();
        builder.part("file", new ClassPathResource("test.pdf"));
        builder.part("fileLanguage", "en_US");
        builder.part("translationLanguage", "en_US");
        builder.part("voiceID", "male_v1");
        builder.part("splittingID", "DOCUMENT");

        NewJobRecord newJob = webClient.post().uri("/jobs")
                .cookie(cookie.getName(), cookie.getValue())
                .body(BodyInserters.fromMultipartData(builder.build()))
                .exchange()
                .expectStatus().isAccepted()
                .expectBody(NewJobRecord.class)
                .returnResult().getResponseBody();

        assertThat(newJob).isNotNull();

        Job job = jobService.getJobByJobId(newJob.jobID());
        String filePath = "/opt/librime/files/test/test.mp3";
        new File("/opt/librime/files/test/").mkdirs();
        Files.copy(Paths.get(System.getProperty("user.dir"),"src/test/resources/test.mp3"), Paths.get(filePath), StandardCopyOption.REPLACE_EXISTING);
        job.setOutputFilePath(filePath);
        jobService.updateJob(job);

        webClient.get().uri("/jobs/"+newJob.jobID()+"/result")
                .cookie(cookie.getName(), cookie.getValue())
                .exchange()
                .expectHeader().contentType("audio/mpeg")
                .expectStatus()
                .isOk();
    }

    @Test
    void ForbiddenAccessTest() throws IOException {
        ResponseCookie cookieA = getSessionCookie();
        
        MultipartBodyBuilder builder = new MultipartBodyBuilder();
        builder.part("file", new ClassPathResource("test.pdf"));
        builder.part("fileLanguage", "en_US");
        builder.part("translationLanguage", "en_US");
        builder.part("voiceID", "male_v1");
        builder.part("splittingID", "DOCUMENT");

        NewJobRecord jobA = webClient.post().uri("/jobs")
                .cookie(cookieA.getName(), cookieA.getValue())
                .body(BodyInserters.fromMultipartData(builder.build()))
                .exchange()
                .expectStatus().isAccepted()
                .expectBody(NewJobRecord.class)
                .returnResult().getResponseBody();

        ResponseCookie cookieB = getSessionCookie();
        
        webClient.get().uri("/jobs/"+jobA.jobID())
                .cookie(cookieB.getName(), cookieB.getValue())
                .exchange()
                .expectStatus()
                .isForbidden();
    }

    @Test
    void JwtSessionPersistenceTest() {
        FluxExchangeResult<Object> result1 = webClient.get().uri("/jobs")
                .exchange()
                .expectStatus().isOk()
                .returnResult(Object.class);

        ResponseCookie cookie1 = result1.getResponseCookies().getFirst("libriME_jwt");
        assertThat(cookie1).isNotNull();

        webClient.get().uri("/jobs")
                .cookie(cookie1.getName(), cookie1.getValue())
                .exchange()
                .expectStatus().isOk()
                .expectHeader().doesNotExist("Set-Cookie");
    }

    @Test
    void JwtOnFirstPostTest() {
        MultipartBodyBuilder builder = new MultipartBodyBuilder();
        builder.part("file", new ClassPathResource("test.pdf"));
        builder.part("fileLanguage", "en_US");
        builder.part("translationLanguage", "en_US");
        builder.part("voiceID", "male_v1");
        builder.part("splittingID", "DOCUMENT");

        FluxExchangeResult<NewJobRecord> result = webClient.post().uri("/jobs")
                .body(BodyInserters.fromMultipartData(builder.build()))
                .exchange()
                .expectStatus().isAccepted()
                .returnResult(NewJobRecord.class);

        ResponseCookie cookie = result.getResponseCookies().getFirst("libriME_jwt");
        assertThat(cookie).isNotNull();
        assertThat(cookie.getValue()).isNotEmpty();
    }
}
