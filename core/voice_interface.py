import asyncio
import speech_recognition as sr
import pyttsx3
from typing import Dict, Any, Callable, List
from utils.logger import logger

class VoiceInterface:
    """
    Provides voice input (Speech-to-Text) and output (Text-to-Speech) capabilities for JARVIS AI.
    """
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.voice_enabled = config.get("VOICE_ENABLED", False)
        self.wake_word = config.get("WAKE_WORD", "jarvis").lower()
        self.stt_model = config.get("STT_MODEL", "tiny.en") # Whisper model
        self.tts_voice = config.get("TTS_VOICE", "en-US")

        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.tts_engine = None
        self._init_tts_engine()

        self.is_listening = False
        self.is_speaking = False
        self.registered_commands: Dict[str, Callable] = {}

        if self.voice_enabled:
            logger.info(f"Voice Interface initialized. Wake word: '{self.wake_word}', STT: {self.stt_model}, TTS: {self.tts_voice}")
        else:
            logger.info("Voice Interface is disabled in configuration.")

    def _init_tts_engine(self):
        """Initializes the Text-to-Speech engine."""
        try:
            self.tts_engine = pyttsx3.init()
            voices = self.tts_engine.getProperty('voices')
            # Try to find a voice that matches the configured TTS_VOICE
            found_voice = False
            for voice in voices:
                if self.tts_voice in voice.id:
                    self.tts_engine.setProperty('voice', voice.id)
                    found_voice = True
                    break
            if not found_voice:
                logger.warning(f"TTS voice '{self.tts_voice}' not found. Using default voice.")
            
            self.tts_engine.setProperty('rate', 180) # Speed of speech
            self.tts_engine.setProperty('volume', 1.0) # Volume (0.0 to 1.0)
            logger.info("TTS engine initialized.")
        except Exception as e:
            logger.error(f"Failed to initialize TTS engine: {e}. Voice output will be unavailable.")
            self.tts_engine = None

    def register_command_callback(self, command_phrase: str, callback: Callable):
        """Registers a callback function for a specific voice command."""
        self.registered_commands[command_phrase.lower()] = callback
        logger.info(f"Registered voice command: '{command_phrase}'")

    async def start_listening(self, continuous: bool = False):
        """
        Starts listening for voice input.
        If continuous is True, it listens indefinitely.
        """
        if not self.voice_enabled:
            logger.warning("Voice interface is disabled. Cannot start listening.")
            return

        self.is_listening = True
        logger.info("Starting voice listening...")
        
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source) # Adjust for noise once
            logger.info("Adjusted for ambient noise. Say something!")
            
            while self.is_listening:
                try:
                    audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
                    text = self.recognizer.recognize_whisper(audio, model=self.stt_model)
                    logger.debug(f"Heard: '{text}'")
                    
                    if self.wake_word in text.lower():
                        logger.info(f"Wake word '{self.wake_word}' detected!")
                        await self.speak("Yes, how can I help?")
                        # Listen for the actual command after wake word
                        command_audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
                        command_text = self.recognizer.recognize_whisper(command_audio, model=self.stt_model)
                        logger.info(f"Command heard: '{command_text}'")
                        
                        # Process command
                        await self._process_voice_command(command_text)
                    
                    if not continuous:
                        break # Stop after one command if not continuous

                except sr.WaitTimeoutError:
                    logger.debug("No speech detected within timeout.")
                except sr.UnknownValueError:
                    logger.warning("Could not understand audio.")
                except sr.RequestError as e:
                    logger.error(f"Could not request results from STT service; {e}")
                except Exception as e:
                    logger.error(f"An unexpected error occurred during listening: {e}")
        
        self.is_listening = False
        logger.info("Stopped listening.")

    async def _process_voice_command(self, command_text: str):
        """Processes a recognized voice command."""
        command_text_lower = command_text.lower()
        found_command = False
        for phrase, callback in self.registered_commands.items():
            if phrase in command_text_lower:
                logger.info(f"Executing command: '{phrase}'")
                await callback(command_text) # Pass the full command text to the callback
                found_command = True
                break
        
        if not found_command:
            await self.speak("I didn't understand that command. Please try again.")
            logger.warning(f"Unrecognized voice command: '{command_text}'")

    async def _single_voice_input(self, prompt: str = "") -> str:
        """Gets a single voice input from the user."""
        if not self.voice_enabled:
            logger.warning("Voice interface is disabled. Cannot get voice input.")
            return ""

        if prompt:
            await self.speak(prompt)
            
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source)
            logger.info("Listening for input...")
            try:
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
                text = self.recognizer.recognize_whisper(audio, model=self.stt_model)
                logger.info(f"Heard: '{text}'")
                return text
            except sr.WaitTimeoutError:
                logger.warning("No speech detected within timeout.")
                return ""
            except sr.UnknownValueError:
                logger.warning("Could not understand audio.")
                return ""
            except sr.RequestError as e:
                logger.error(f"Could not request results from STT service; {e}")
                return ""
            except Exception as e:
                logger.error(f"An unexpected error occurred during single voice input: {e}")
                return ""

    async def speak(self, text: str):
        """Converts text to speech and plays it."""
        if not self.voice_enabled or not self.tts_engine:
            logger.warning("Voice output is disabled or TTS engine not initialized.")
            return

        self.is_speaking = True
        logger.info(f"JARVIS speaking: '{text}'")
        try:
            # pyttsx3 runAndWait() is blocking, so run it in a separate thread/executor
            # to avoid blocking the asyncio event loop.
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self._speak_blocking, text)
        except Exception as e:
            logger.error(f"Error during TTS playback: {e}")
        finally:
            self.is_speaking = False

    def _speak_blocking(self, text: str):
        """Blocking call for pyttsx3.runAndWait()."""
        if self.tts_engine:
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()

    def stop_listening(self):
        """Stops the continuous listening process."""
        self.is_listening = False
        logger.info("Voice listening stopped.")

    def get_voice_stats(self) -> Dict[str, Any]:
        """Returns the current status and configuration of the voice interface."""
        return {
            "voice_enabled": self.voice_enabled,
            "is_listening": self.is_listening,
            "is_speaking": self.is_speaking,
            "wake_word": self.wake_word,
            "stt_model": self.stt_model,
            "tts_voice": self.tts_voice,
            "registered_commands": list(self.registered_commands.keys())
        }
