package org.librime.libribackend.restservice.Records;

import org.librime.libribackend.Types.StatusType;
import java.util.UUID;

public record StatusJobRecord(UUID jobID,
                              StatusType status,
                              int progress,
                              String downloadURL,
                              String error) implements JobRecord {
}
