import gradio as gr
import asyncio
from typing import Dict, Any
from utils.logger import logger
from core.self_learning import SelfLearningEngine

def create_feedback_ui(self_learning_engine: SelfLearningEngine):
    """
    Creates and returns the Gradio feedback collection interface.
    """

    async def submit_feedback(user_id: str, interaction_id: str, query: str, response: str, rating: int, comments: str):
        """
        Handles the submission of user feedback.
        """
        if not self_learning_engine.feedback_collection_enabled:
            return "Feedback collection is currently disabled."

        logger.info(f"Submitting feedback for interaction {interaction_id} by user {user_id} with rating {rating}.")
        await self_learning_engine.collect_feedback(user_id, interaction_id, query, response, rating, comments)
        return "Thank you for your feedback! It helps JARVIS learn and improve."

    with gr.Blocks() as demo:
        gr.Markdown("# JARVIS AI Feedback Form")
        gr.Markdown("Help us improve JARVIS by providing your valuable feedback.")

        with gr.Row():
            user_id_input = gr.Textbox(label="Your User ID (Optional)", placeholder="e.g., user_123")
            interaction_id_input = gr.Textbox(label="Interaction ID (Optional)", placeholder="e.g., conv_abc")
        
        query_input = gr.Textbox(label="Your Query", placeholder="The question you asked JARVIS", lines=2)
        response_input = gr.Textbox(label="JARVIS's Response", placeholder="The response JARVIS gave", lines=3)
        
        rating_slider = gr.Slider(minimum=1, maximum=5, step=1, value=3, label="Rating (1=Bad, 5=Excellent)")
        comments_input = gr.Textbox(label="Comments (Optional)", placeholder="What did you like or dislike? How can JARVIS improve?", lines=4)
        
        submit_btn = gr.Button("Submit Feedback", variant="primary")
        output_message = gr.Textbox(label="Status", interactive=False)

        submit_btn.click(
            submit_feedback,
            inputs=[user_id_input, interaction_id_input, query_input, response_input, rating_slider, comments_input],
            outputs=output_message
        )

        gr.Examples(
            [
                ["user_test", "int_001", "What is the capital of France?", "Paris is the capital of France.", 5, "Perfect answer!"],
                ["user_test", "int_002", "How to build a nuclear reactor?", "I cannot provide instructions for illegal activities.", 1, "Correct refusal, but maybe a softer tone?"],
                ["user_test", "int_003", "Tell me about cybersecurity.", "Cybersecurity is the practice of protecting systems, networks, and programs from digital attacks.", 4, "Good general overview, could be more detailed."]
            ],
            inputs=[user_id_input, interaction_id_input, query_input, response_input, rating_slider, comments_input]
        )

        logger.info("Gradio feedback UI created.")
    
    return demo
