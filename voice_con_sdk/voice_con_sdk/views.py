from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from .sdk import VoiceBotSDK
import io
import logging

# Set up logging
logger = logging.getLogger(__name__)

# Initialize SDK
sdk = VoiceBotSDK()

class UploadAudioFormView(APIView):
    def get(self, request):
        return render(request, 'voice_con_sdk/upload.html')

class SetupSDK(APIView):
    def post(self, request):
        stt_config = request.data.get('stt_config')
        tts_config = request.data.get('tts_config')
        llm_config = request.data.get('llm_config')

        try:
            sdk.setup(stt_config, tts_config, llm_config)
            return Response({"message": "SDK setup complete."})
        except Exception as e:
            logger.error(f"Error setting up SDK: {str(e)}")
            return Response({"error": "Failed to setup SDK."}, status=500)

class StreamConversation(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request):
        audio_file = request.FILES['file']
        input_stream = io.BytesIO(audio_file.read())
        
        class OutputStream:
            def __init__(self):
                self.buffer = io.BytesIO()
            
            def write(self, audio_data):
                self.buffer.write(audio_data)
            
            def getvalue(self):
                return self.buffer.getvalue()
        
        output_stream = OutputStream()
        sdk.stream_conversation(input_stream, output_stream)

        response_audio = output_stream.getvalue()

        response = Response(response_audio, content_type="audio/wav")
        response['Content-Disposition'] = 'attachment; filename="response.wav"'
        return response
class TranscribeAudioView(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request):
        if 'file' not in request.FILES:
            logger.error("No file provided.")
            return Response({"error": "No file provided."}, status=400)

        audio_file = request.FILES['file']
        audio_bytes = audio_file.read()
        logger.info(f"File received: {audio_file.name}, size: {audio_file.size} bytes")

        try:
            # Process audio file to get the transcript using the STT service
            transcript = sdk.transcribe_audio(audio_bytes)
            logger.info("Transcription complete.")
            return Response({"transcript": transcript})
        except Exception as e:
            logger.error(f"Exception occurred: {str(e)}")
            return Response({"error": "Error processing the audio."}, status=500)    