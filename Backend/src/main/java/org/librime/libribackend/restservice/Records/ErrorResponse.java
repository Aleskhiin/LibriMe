package org.librime.libribackend.restservice.Records;

import java.time.LocalDateTime;

public record ErrorResponse(
        int status,
        String message,
        LocalDateTime timestamp,
        String path
) {}
