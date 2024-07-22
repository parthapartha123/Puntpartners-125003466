from deepgram import Deepgram
import openai
from gtts import gTTS
import io
import logging

# Configure logger
logger = logging.getLogger('voice_con_sdk') 

class VoiceBotSDK:
    def __init__(self):
        self.stt_client = None
        self.tts_client = None
        self.llm_client = None

    def setup(self, stt_config, tts_config, llm_config):
        # Initialize STT
        if stt_config['name'] == 'Deepgram':
            self.stt_client = Deepgram(stt_config['api_key'])
        
        # Initialize TTS and LLM
        if tts_config['name'] in ['OpenAI', 'Deepgram', 'gTTS']:
            self.tts_client = tts_config
        
        if llm_config['name'] == 'OpenAI':
            openai.api_key = llm_config['api_key']
            self.llm_client = openai

        self.system_prompt = llm_config['system_prompt']

    def transcribe_audio(self, audio_stream):
        try:
            response = self.stt_client.transcription.prerecorded(
                {'buffer': audio_stream, 'mimetype': 'audio/wav'},
                {'punctuate': True}
            )
            if response and 'results' in response and 'channels' in response['results']:
                return response['results']['channels'][0]['alternatives'][0]['transcript']
            else:
                logger.error("Unexpected response structure from STT service.")
                return None
        except Exception as e:
            logger.error(f"Exception occurred during transcription: {str(e)}")
            return None

    def query_llm(self, text):
        try:
            response = openai.Completion.create(
                engine="text-davinci-003",
                prompt=f"{self.system_prompt}\n\nUser: {text}\nAI:",
                max_tokens=150
            )
            return response.choices[0].text.strip()
        except Exception as e:
            logger.error(f"Exception occurred during LLM query: {str(e)}")
            return "Error querying LLM."

    def synthesize_speech(self, text):
        try:
            tts = gTTS(text, lang='en')
            audio_stream = io.BytesIO()
            tts.write_to_fp(audio_stream)
            audio_stream.seek(0)
            return audio_stream.getvalue()
        except Exception as e:
            logger.error(f"Exception occurred during TTS synthesis: {str(e)}")
            return None

    def stream_conversation(self, input_stream, output_stream):
        try:
            audio_data = input_stream.read()
            transcript = self.transcribe_audio(audio_data)
            if transcript:
                llm_response = self.query_llm(transcript)
                tts_audio = self.synthesize_speech(llm_response)
                if tts_audio:
                    output_stream.write(tts_audio)
                else:
                    logger.error("Failed to synthesize speech.")
            else:
                logger.error("Failed to transcribe audio.")
        except Exception as e:
            logger.error(f"Exception occurred during conversation streaming: {str(e)}")
