import asyncio
import speech_recognition as sr
from gtts import gTTS
import os
import sys # Added for platform check
from typing import Dict, Any
from utils.logger import logger

class VoiceInterface:
    """
    Manages the voice input and output for JARVIS AI.
    Includes Speech-to-Text (STT) and Text-to-Speech (TTS) functionalities.
    """
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.enabled = config.get("enabled", False)
        self.wake_word = config.get("wake_word", "jarvis").lower()
        self.stt_model = config.get("stt_model", "tiny.en") # e.g., "tiny.en", "base.en", "small.en" for Whisper
        self.tts_voice = config.get("tts_voice", "en-US") # e.g., "en-US", "en-GB"

        if self.enabled:
            self.recognizer = sr.Recognizer()
            # Placeholder for actual Whisper model loading if using local Whisper
            # self.whisper_model = whisper.load_model(self.stt_model)
            logger.info(f"Voice Interface initialized. Wake word: '{self.wake_word}', STT model: '{self.stt_model}'")
        else:
            logger.info("Voice Interface is disabled in configuration.")

    async def listen_for_wake_word(self) -> bool:
        """
        Listens for the wake word. This is a blocking operation in real-time.
        For simulation, it will just return True after a delay.
        """
        if not self.enabled:
            return False

        logger.info(f"Listening for wake word: '{self.wake_word}' (simulated)...")
        await asyncio.sleep(3) # Simulate listening time
        logger.info("Wake word detected (simulated).")
        return True

    async def transcribe_speech(self) -> str:
        """
        Captures audio input and transcribes it to text.
        """
        if not self.enabled:
            return "Voice input disabled."

        logger.info("Listening for speech input...")
        try:
            with sr.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source)
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=5)
            
            # Use Google Web Speech API for simplicity, or integrate local Whisper
            text = self.recognizer.recognize_google(audio)
            logger.info(f"Transcribed: '{text}'")
            return text
        except sr.UnknownValueError:
            logger.warning("Could not understand audio.")
            return ""
        except sr.RequestError as e:
            logger.error(f"Could not request results from Google Speech Recognition service; {e}")
            return ""
        except asyncio.TimeoutError:
            logger.warning("No speech detected within timeout.")
            return ""
        except Exception as e:
            logger.error(f"An error occurred during speech transcription: {e}")
            return ""

    async def speak(self, text: str):
        """
        Converts text to speech and plays it.
        """
        if not self.enabled:
            logger.info(f"Voice output disabled. Would have said: '{text}'")
            return

        logger.info(f"Speaking: '{text}'")
        try:
            tts = gTTS(text=text, lang=self.tts_voice.split('-')[0], slow=False)
            audio_file = "jarvis_response.mp3"
            tts.save(audio_file)
            
            # Play the audio file (platform-dependent)
            if sys.platform == "darwin": # macOS
                os.system(f"afplay {audio_file}")
            elif sys.platform == "win32": # Windows
                os.system(f"start {audio_file}")
            else: # Linux
                os.system(f"mpg123 {audio_file}") # Requires mpg123 to be installed

            os.remove(audio_file) # Clean up
            logger.debug("Speech playback complete.")
        except Exception as e:
            logger.error(f"Error during text-to-speech: {e}")
