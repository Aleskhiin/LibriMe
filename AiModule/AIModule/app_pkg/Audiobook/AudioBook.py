from abc import ABC, abstractmethod

class AudioBook():
    def __init__(self, documentPath, language, processId, feature, voice):
        self.documentPath = documentPath
        self.language = language
        self.processId = processId
        self.feature = feature
        self.voice = voice

    @abstractmethod
    async def createAudioBook(self):
        pass