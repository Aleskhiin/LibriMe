package org.librime.libribackend.MQHandler.MessageRecords;

import org.librime.libribackend.Types.LanguageType;
import org.librime.libribackend.Types.SplittingType;
import org.librime.libribackend.Types.StatusType;
import org.librime.libribackend.Types.VoiceType;

import java.util.UUID;

public record RunningJobMessage(UUID jobID,
                                StatusType status,
                                int progress,
                                String resultPath) implements JobMessage {
}
