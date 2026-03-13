package org.librime.libribackend.restservice.Records;

import org.librime.libribackend.Types.StatusType;
import java.util.UUID;

public record NewJobRecord(UUID jobID,
                           StatusType status,
                           String message,
                           String StatusURL) implements JobRecord {
}
