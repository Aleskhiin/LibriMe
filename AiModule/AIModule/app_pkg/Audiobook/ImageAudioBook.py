from AudioBook import AudioBook

class ImageAudioBook(AudioBook):
    def __init__(self, documentPath, language, ProcessId, feature, format):
        super().__init__(documentPath, language, ProcessId, feature)
        self.format = format

    async def process(self):
        # Implementation for processing image commands
        pass
    