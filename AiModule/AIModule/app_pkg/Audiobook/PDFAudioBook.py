from AudioBook import AudioBook

class PDFAudioBook(AudioBook):
    def __init__(self, documentPath, language, processId, feature, processMode):
        super().__init__(documentPath, language, processId, feature)
        self.processMode = processMode

    async def process(self):
        # Implementation for processing image commands
        pass