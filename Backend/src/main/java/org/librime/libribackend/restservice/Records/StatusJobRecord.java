package org.librime.libribackend.restservice.Records;

import org.librime.libribackend.Types.StatusType;
import org.librime.libribackend.Types.LanguageType;
import org.librime.libribackend.Types.VoiceType;
import org.librime.libribackend.Types.SplittingType;
import java.util.UUID;

public record StatusJobRecord(UUID jobID,
                              StatusType status,
                              int progress,
                              String downloadURL,
                              String error,
                              String fileName,
                              LanguageType fileLanguage,
                              LanguageType translationLanguage,
                              VoiceType voiceID,
                              SplittingType splittingID) implements JobRecord {
}
