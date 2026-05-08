package org.librime.libribackend;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.librime.libribackend.DBAccess.JobService;
import org.librime.libribackend.DBAccess.Model.Job;
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
import org.springframework.test.web.reactive.server.WebTestClient;
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
        createNullJob();
    }

    void createNullJob() throws IOException, InterruptedException {
        if(jobService.hasJobByJobId(UUID.fromString(dummyUUID))){
            jobService.updateJobStatus(UUID.fromString(dummyUUID), StatusType.QUEUED);
            jobService.updateJobProgress(UUID.fromString(dummyUUID), 0);
        }else{
            //String filePath = System.getProperty("user.dir")+"/librime/files/test/";
            String filePath = "/opt/librime/files/test/";
            File file = new File(filePath);
            file.mkdirs();

            jobService.createJob(new Job(UUID.fromString(dummyUUID), filePath+"test.pdf", VoiceType.male_v1, SplittingType.DOCUMENT, LanguageType.en_US, LanguageType.en_US, StatusType.QUEUED));
            Files.copy(Paths.get(System.getProperty("user.dir"),"src/test/resources/test.mp3"), Paths.get(filePath, "test.mp3"), StandardCopyOption.REPLACE_EXISTING);
            Files.copy(Paths.get(System.getProperty("user.dir"),"src/test/resources/test.pdf"), Paths.get(filePath, "test.pdf"), StandardCopyOption.REPLACE_EXISTING);
            Thread.sleep(1000); //try more elegant later
            jobService.updateJobResultPath(UUID.fromString(dummyUUID), filePath+"test.mp3");
        }
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
    void GetJobStatusTest() {
        webClient.get().uri("/jobs/"+dummyUUID)
                .exchange()
                .expectStatus()
                .isOk();
    }

    @Test
    void  GetJobResultTest() {
        webClient.get().uri("/jobs/"+dummyUUID+"/result")
                .exchange()
                .expectHeader().contentType("audio/mpeg")
                .expectStatus()
                .isOk();
    }
//    @Test
//    void RabbitMQshouldSendAndConsumeMessageTest() throws Exception {
//        // given
//        String payload = "test";
//
//        // when: send GET request to REST endpoint
//        webClient.get()
//                .uri(uriBuilder -> uriBuilder
//                        .path("/queueHelloWorld")
//                        .queryParam("text", payload)
//                        .build())
//                .exchange()
//                .expectStatus().isOk();
//
//        // then: verify the message was consumed
//        HelloWorld received = rabbitMQListener.takeMessage();
//        assertThat(received).isEqualTo(new HelloWorld(String.format("Hello, %s!", payload)));
//    }

//    @Test
//    void HelloWorldEndtoEndTest(){
//        webClient.get().uri("/helloWorld")
//                .exchange()
//                .expectStatus().isOk();
//    }
}
