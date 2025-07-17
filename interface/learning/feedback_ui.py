import gradio as gr
import asyncio
from typing import Any, Tuple
from utils.logger import logger

class FeedbackUI:
    """
    Gradio-based UI for JARVIS AI's Self-Learning Engine, specifically for user feedback.
    """
    def __init__(self, learning_engine: Any): # Use Any to avoid circular imports
        self.learning_engine = learning_engine
        logger.info("Feedback UI initialized.")

    async def submit_feedback(self, user_input: str, jarvis_response: str, feedback_type: str, rating: float) -> str:
        """
        Submits user feedback to the learning engine.
        """
        if not user_input or not jarvis_response:
            return "Please provide both user input and JARVIS's response."

        logger.info(f"Submitting feedback: Type={feedback_type}, Rating={rating}")
        
        feedback_id = await self.learning_engine.process_user_feedback(
            user_input=user_input,
            jarvis_response=jarvis_response,
            feedback_type=feedback_type,
            rating=rating
        )
        
        if feedback_id != "error":
            return f"Feedback submitted successfully! ID: {feedback_id}"
        else:
            return "Failed to submit feedback. Please check logs."

    async def trigger_scraping(self) -> str:
        """
        Triggers the security data scraping process.
        """
        logger.info("Triggering security data scraping from UI.")
        results = await self.learning_engine.scrape_security_data()
        return f"Scraping initiated. Total scraped: {results.get('total_scraped', 0)}, New knowledge: {results.get('new_knowledge', 0)}"

    async def trigger_optimization(self) -> str:
        """
        Triggers the learning parameter optimization process.
        """
        logger.info("Triggering learning parameter optimization from UI.")
        results = await self.learning_engine.optimize_learning_parameters()
        return f"Optimization initiated. Status: {results.get('status', 'unknown')}"

    def create_interface(self):
        """Creates and returns the Gradio Blocks interface for feedback and learning controls."""
        with gr.Blocks(title="JARVIS AI - Self-Learning & Feedback", theme=gr.themes.Soft()) as feedback_ui:
            gr.Markdown("# 🧠 JARVIS AI - Self-Learning & Feedback")
            gr.Markdown("Help JARVIS learn and improve by providing feedback and managing knowledge acquisition.")

            with gr.Tab("Provide Feedback"):
                gr.Markdown("## User Feedback Form")
                user_input_text = gr.Textbox(label="Your Input to JARVIS", placeholder="e.g., 'Analyze this log file.'")
                jarvis_response_text = gr.Textbox(label="JARVIS's Response", placeholder="e.g., 'I found suspicious activity.'")
                
                feedback_type_radio = gr.Radio(
                    choices=["thumbs_up", "thumbs_down", "correction", "suggestion"],
                    label="Feedback Type",
                    value="thumbs_up"
                )
                rating_slider = gr.Slider(minimum=0, maximum=1, step=0.1, value=0.8, label="Rating (0.0 - 1.0)")
                
                submit_feedback_btn = gr.Button("Submit Feedback", variant="primary")
                feedback_status_output = gr.Textbox(label="Status", interactive=False)

                submit_feedback_btn.click(
                    fn=self.submit_feedback,
                    inputs=[user_input_text, jarvis_response_text, feedback_type_radio, rating_slider],
                    outputs=[feedback_status_output]
                )
            
            with gr.Tab("Knowledge Acquisition"):
                gr.Markdown("## Knowledge Acquisition & Optimization")
                gr.Markdown("Manually trigger data scraping or learning parameter optimization.")
                
                scrape_btn = gr.Button("Scrape Security Data Now", variant="secondary")
                scrape_status_output = gr.Textbox(label="Scraping Status", interactive=False)
                
                optimize_btn = gr.Button("Optimize Learning Parameters", variant="secondary")
                optimize_status_output = gr.Textbox(label="Optimization Status", interactive=False)

                scrape_btn.click(
                    fn=self.trigger_scraping,
                    outputs=[scrape_status_output]
                )
                
                optimize_btn.click(
                    fn=self.trigger_optimization,
                    outputs=[optimize_status_output]
                )

            gr.Markdown("---")
            gr.Markdown("Powered by JARVIS AI - Phase 3: Self-Learning")

        return feedback_ui
