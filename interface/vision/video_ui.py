import gradio as gr
import asyncio
from typing import Any, Dict, Tuple
from utils.logger import logger

class VideoUI:
    """
    Gradio-based UI for JARVIS AI's Vision Engine.
    Allows users to upload videos for analysis.
    """
    def __init__(self, vision_engine: Any): # Use Any to avoid circular imports
        self.vision_engine = vision_engine
        logger.info("Video UI initialized.")

    async def analyze_uploaded_video(self, video_file_path: str) -> Tuple[str, str]:
        """
        Handles video upload and triggers analysis.
        """
        if not video_file_path:
            return "Please upload a video file.", ""

        logger.info(f"Received video for analysis: {video_file_path}")
        
        # Trigger analysis in the Vision Engine
        analysis_result = await self.vision_engine.analyze_video(video_file_path)
        
        if analysis_result.get("status") == "completed":
            summary = analysis_result.get("summary", "Analysis completed.")
            details = f"Video Path: {analysis_result.get('video_path')}\n" \
                      f"Total Frames: {analysis_result.get('total_frames')}\n" \
                      f"Duration: {analysis_result.get('analysis_duration_seconds'):.2f} seconds\n" \
                      f"Detected Objects: {analysis_result.get('detected_objects')}\n" \
                      f"Anomalies Detected: {analysis_result.get('anomalies_detected')}"
            logger.info(f"Video analysis successful: {summary}")
            return summary, details
        else:
            error_msg = analysis_result.get("reason", "Unknown error during analysis.")
            logger.error(f"Video analysis failed: {error_msg}")
            return f"Video analysis failed: {error_msg}", ""

    def create_interface(self):
        """Creates and returns the Gradio Blocks interface for video analysis."""
        with gr.Blocks(title="JARVIS AI - Video Analysis", theme=gr.themes.Soft()) as video_ui:
            gr.Markdown("# 👁️ JARVIS AI - Video Analysis")
            gr.Markdown("Upload a video file for automated security and anomaly detection.")

            with gr.Row():
                video_input = gr.Video(label="Upload Video", type="filepath")
                
            with gr.Row():
                analyze_btn = gr.Button("Analyze Video", variant="primary")
                clear_btn = gr.Button("Clear")

            analysis_summary = gr.Textbox(label="Analysis Summary", interactive=False, lines=2)
            analysis_details = gr.Textbox(label="Analysis Details", interactive=False, lines=10)

            analyze_btn.click(
                fn=self.analyze_uploaded_video,
                inputs=[video_input],
                outputs=[analysis_summary, analysis_details]
            )
            
            clear_btn.click(
                lambda: (None, "", ""), # Clear video, summary, and details
                outputs=[video_input, analysis_summary, analysis_details]
            )

            gr.Examples(
                examples=[
                    "data/video_datasets/sample_security_footage.mp4",
                    "data/video_datasets/sample_network_traffic.pcap"
                ],
                inputs=video_input,
                label="Example Video Files (ensure these files exist)"
            )

            gr.Markdown("---")
            gr.Markdown("Powered by JARVIS AI - Phase 2: Vision & Knowledge Integration")

        return video_ui
