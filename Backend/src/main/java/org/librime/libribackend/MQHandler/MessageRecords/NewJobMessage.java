package org.librime.libribackend.MQHandler.MessageRecords;

import org.librime.libribackend.Types.LanguageType;
import org.librime.libribackend.Types.SplittingType;
import org.librime.libribackend.Types.VoiceType;
import java.util.UUID;

public record NewJobMessage(UUID jobID,
                            LanguageType fileLanguage,
                            LanguageType translationLanguage,
                            VoiceType voiceID,
                            String dataPath,
                            SplittingType splittingType) implements JobMessage {
}
