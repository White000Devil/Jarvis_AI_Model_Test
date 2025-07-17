import gradio as gr
import asyncio
from typing import List, Tuple, Dict, Any
from utils.logger import logger

class ChatInterface:
    """
    Gradio-based chat interface for JARVIS AI.
    """
    def __init__(self, jarvis_ai_instance: Any): # Use Any to avoid circular imports
        self.jarvis_ai = jarvis_ai_instance
        self.chat_history: List[Tuple[str, str]] = []
        logger.info("Chat Interface initialized.")

    async def respond(self, message: str, chat_history: List[Tuple[str, str]]) -> Tuple[str, List[Tuple[str, str]]]:
        """
        Handles user input, gets JARVIS's response, and updates chat history.
        """
        logger.info(f"User message: {message}")
        self.chat_history = chat_history # Update internal history with Gradio's
        
        # Get JARVIS's response
        jarvis_response = await self.jarvis_ai.chat(message)
        
        # Update chat history
        self.chat_history.append((message, jarvis_response))
        logger.info(f"JARVIS response: {jarvis_response}")
        
        return "", self.chat_history # Clear input box and return updated history

    def create_interface(self):
        """Creates and returns the Gradio Blocks interface."""
        with gr.Blocks(title="JARVIS AI Chat", theme=gr.themes.Soft()) as chat_interface:
            gr.Markdown("# 🤖 JARVIS AI Assistant")
            gr.Markdown("Your intelligent assistant for security, operations, and more.")

            chatbot = gr.Chatbot(
                label="Conversation",
                height=500,
                avatar_images=(
                    "https://raw.githubusercontent.com/gradio-app/gradio/main/guides/assets/logo.png", # User avatar
                    "https://i.imgur.com/0o25QyQ.png" # JARVIS avatar (example)
                )
            )
            msg = gr.Textbox(label="Your Message", placeholder="Type your message here...")
            
            with gr.Row():
                submit_btn = gr.Button("Send", variant="primary")
                clear_btn = gr.Button("Clear Chat")

            # Event handlers
            submit_btn.click(
                fn=self.respond,
                inputs=[msg, chatbot],
                outputs=[msg, chatbot],
                queue=False # Process immediately
            )
            msg.submit( # Allow pressing Enter to submit
                fn=self.respond,
                inputs=[msg, chatbot],
                outputs=[msg, chatbot],
                queue=False
            )
            clear_btn.click(
                lambda: ([], ""), # Clear chat history and input box
                outputs=[chatbot, msg],
                queue=False
            )
            
            gr.Examples(
                examples=[
                    "Hello JARVIS, how are you?",
                    "What is a SQL injection vulnerability?",
                    "Can you help me deploy a new service?",
                    "Analyze the video footage from 'sample_security_footage.mp4'.",
                    "I have some feedback for you.",
                    "Let's start a collaboration session."
                ],
                inputs=msg,
                label="Quick Examples"
            )

            gr.Markdown("---")
            gr.Markdown("Powered by JARVIS AI - Phase 5: Advanced AI & Ethical AI")

        return chat_interface
