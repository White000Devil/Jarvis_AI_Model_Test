import gradio as gr
import asyncio
from typing import TYPE_CHECKING, Dict, Any
from utils.logger import logger
from core.vision_engine import VisionEngine
from datetime import datetime

# To avoid circular imports for type hinting
if TYPE_CHECKING:
    from core.vision_engine import VisionEngine

class VideoUI:
    """
    Gradio-based interface for JARVIS AI's video analysis capabilities.
    """
    def __init__(self, vision_engine: "VisionEngine"):
        self.vision_engine = vision_engine

    async def analyze_image_ui(self, image_file) -> Dict[str, Any]:
        """
        Handles image analysis requests from the UI.
        """
        if not self.vision_engine:
            return {"status": "error", "message": "Vision Engine not initialized."}
        if not image_file:
            return {"status": "error", "message": "No image file provided."}
        
        try:
            # Gradio's File component provides a temp file path
            image_path = image_file.name
            results = await self.vision_engine.analyze_image(image_path)
            return results
        except Exception as e:
            return {"status": "error", "message": f"Error analyzing image: {e}"}

    async def analyze_video_stream_ui(self, stream_url: str, duration: int) -> Dict[str, Any]:
        """
        Handles video stream analysis requests from the UI.
        """
        if not self.vision_engine:
            return {"status": "error", "message": "Vision Engine not initialized."}
        if not stream_url:
            return {"status": "error", "message": "No stream URL provided."}
        
        try:
            results = await self.vision_engine.analyze_video_stream(stream_url, duration)
            return results
        except Exception as e:
            return {"status": "error", "message": f"Error analyzing video stream: {e}"}

    async def identify_face_ui(self, image_file) -> Dict[str, Any]:
        """
        Handles face identification requests from the UI.
        """
        if not self.vision_engine:
            return {"status": "error", "message": "Vision Engine not initialized."}
        if not image_file:
            return {"status": "error", "message": "No image file provided."}
        
        try:
            image_path = image_file.name
            results = await self.vision_engine.identify_face(image_path)
            return results
        except Exception as e:
            return {"status": "error", "message": f"Error identifying face: {e}"}

    async def analyze_video_file_gradio(self, video_file):
        """Handles video file analysis via Gradio."""
        if not self.vision_engine.enabled:
            return "Vision Engine is disabled in configuration."
        if video_file is None:
            return "Please upload a video file."
        
        logger.info(f"Received video file for analysis: {video_file.name}")
        
        # Gradio's File component provides a NamedTemporaryFile object,
        # which has a 'name' attribute for the path.
        results = await self.vision_engine.process_video_file(video_file.name)
        
        if results.get("status") == "success":
            analysis_summary = "Video Analysis Results:\n"
            for frame_data in results["analysis_results"]:
                analysis_summary += f"  Frame {frame_data['frame']} ({frame_data['timestamp']}):\n"
                for obj in frame_data['objects']:
                    analysis_summary += f"    - Detected: {obj['label']} (Confidence: {obj['confidence']:.2f})\n"
            return analysis_summary
        else:
            return f"Video analysis failed: {results.get('message', 'Unknown error')}"

    async def analyze_image_gradio(self, image_file):
        """Handles image file analysis via Gradio."""
        if not self.vision_engine.enabled:
            return "Vision Engine is disabled in configuration."
        if image_file is None:
            return "Please upload an image file."
        
        logger.info(f"Received image file for analysis: {image_file.name}")
        
        results = await self.vision_engine.analyze_image(image_file.name)
        
        if results.get("status") == "success":
            analysis_summary = "Image Analysis Results:\n"
            for obj in results["objects"]:
                analysis_summary += f"  - Detected: {obj['label']} (Confidence: {obj['confidence']:.2f})\n"
                analysis_summary += f"    Bounding Box: {obj['bbox']}\n"
            return analysis_summary
        else:
            return f"Image analysis failed: {results.get('message', 'Unknown error')}"

    async def facial_recognition_gradio(self, image_file):
        """Handles facial recognition via Gradio."""
        if not self.vision_engine.enabled:
            return "Vision Engine is disabled in configuration."
        if image_file is None:
            return "Please upload an image file."
        
        logger.info(f"Received image for facial recognition: {image_file.name}")
        
        results = await self.vision_engine.facial_recognition(image_file.name)
        
        if results.get("status") == "success":
            analysis_summary = "Facial Recognition Results:\n"
            if results["faces"]:
                for face in results["faces"]:
                    analysis_summary += f"  - Name: {face.get('name', 'Unknown')} (Confidence: {face['confidence']:.2f})\n"
                    analysis_summary += f"    Bounding Box: {face['bbox']}\n"
            else:
                analysis_summary += "No faces detected."
            return analysis_summary
        else:
            return f"Facial recognition failed: {results.get('message', 'Unknown error')}"

    def create_interface(self) -> gr.Blocks:
        """
        Creates and returns the Gradio Blocks interface for video analysis.
        """
        with gr.Blocks(title="JARVIS AI Vision Engine") as video_ui:
            gr.Markdown("# JARVIS AI Vision Engine")
            gr.Markdown("Analyze images and video streams using JARVIS's computer vision capabilities.")

            with gr.Tab("Image Analysis"):
                gr.Markdown("## Analyze Image for Objects and Faces")
                image_input = gr.Image(type="filepath", label="Upload Image")
                analyze_image_btn = gr.Button("Analyze Image")
                image_analysis_output = gr.JSON(label="Image Analysis Results")
                
                analyze_image_btn.click(
                    fn=self.analyze_image_ui,
                    inputs=[image_input],
                    outputs=image_analysis_output
                )

            with gr.Tab("Video Stream Analysis"):
                gr.Markdown("## Analyze Video Stream (Mock)")
                stream_url_input = gr.Textbox(label="Video Stream URL (Mock)", placeholder="e.g., rtsp://mock.stream.com/feed1")
                duration_slider = gr.Slider(minimum=5, maximum=60, step=5, value=10, label="Analysis Duration (seconds)")
                analyze_stream_btn = gr.Button("Analyze Stream")
                stream_analysis_output = gr.JSON(label="Video Stream Analysis Results")
                
                analyze_stream_btn.click(
                    fn=self.analyze_video_stream_ui,
                    inputs=[stream_url_input, duration_slider],
                    outputs=stream_analysis_output
                )

            with gr.Tab("Face Identification"):
                gr.Markdown("## Identify Face in Image (Mock)")
                face_image_input = gr.Image(type="filepath", label="Upload Image with Face")
                identify_face_btn = gr.Button("Identify Face")
                face_identification_output = gr.JSON(label="Face Identification Results")
                
                identify_face_btn.click(
                    fn=self.identify_face_ui,
                    inputs=[face_image_input],
                    outputs=face_identification_output
                )

            with gr.Tab("Video File Analysis"):
                gr.Markdown("## Analyze Video File")
                video_input = gr.File(label="Upload Video File", type="file", file_types=[".mp4", ".avi", ".mov"])
                video_output = gr.Textbox(label="Video Analysis Results", interactive=False, lines=10)
                video_btn = gr.Button("Analyze Video")
                video_btn.click(self.analyze_video_file_gradio, inputs=video_input, outputs=video_output)

            with gr.Tab("Facial Recognition"):
                gr.Markdown("## Facial Recognition")
                face_image_input = gr.File(label="Upload Image for Face Recognition", type="file", file_types=[".jpg", ".jpeg", ".png"])
                face_output = gr.Textbox(label="Facial Recognition Results", interactive=False, lines=10)
                face_btn = gr.Button("Perform Facial Recognition")
                face_btn.click(self.facial_recognition_gradio, inputs=face_image_input, outputs=face_output)

        logger.info("Gradio video analysis UI created.")
        return video_ui

# Example of how to run this interface (for testing purposes, main.py handles actual launch)
if __name__ == "__main__":
    # Mock VisionEngine for standalone testing
    class MockVisionEngine:
        def __init__(self, config: Dict[str, Any]):
            self.config = config
            self.enabled = config.get("enabled", True)
            print("Mock Vision Engine initialized.")

        async def analyze_image(self, image_path: str) -> Dict[str, Any]:
            print(f"Mock analyzing image: {image_path}")
            await asyncio.sleep(0.5)
            return {
                "status": "mock_completed",
                "image_path": image_path,
                "objects": [{"label": "mock_object", "confidence": 0.9, "bbox": [10, 20, 30, 40]}],
                "analysis_timestamp": datetime.now().isoformat()
            }

        async def analyze_video_stream(self, stream_url: str, duration_seconds: int = 10) -> Dict[str, Any]:
            print(f"Mock analyzing video stream: {stream_url} for {duration_seconds}s")
            await asyncio.sleep(0.5)
            return {
                "status": "mock_completed",
                "stream_url": stream_url,
                "duration_analyzed_seconds": duration_seconds,
                "analysis_results": [
                    {"frame": 1, "timestamp": "00:00:05", "objects": [{"label": "mock_object", "confidence": 0.9}]}
                ],
                "analysis_timestamp": datetime.now().isoformat()
            }

        async def identify_face(self, image_path: str) -> Dict[str, Any]:
            print(f"Mock identifying face in image: {image_path}")
            await asyncio.sleep(0.5)
            return {
                "status": "mock_completed",
                "image_path": image_path,
                "faces": [{"name": "Mock_Person", "confidence": 0.95, "bbox": [10, 20, 30, 40]}],
                "analysis_timestamp": datetime.now().isoformat()
            }

        async def process_video_file(self, video_path: str) -> Dict[str, Any]:
            print(f"Mock processing video file: {video_path}")
            await asyncio.sleep(0.5)
            return {
                "status": "mock_completed",
                "video_path": video_path,
                "analysis_results": [
                    {"frame": 1, "timestamp": "00:00:05", "objects": [{"label": "mock_object", "confidence": 0.9}]}
                ],
                "analysis_timestamp": datetime.now().isoformat()
            }

        async def facial_recognition(self, image_path: str) -> Dict[str, Any]:
            print(f"Mock performing facial recognition on image: {image_path}")
            await asyncio.sleep(0.5)
            return {
                "status": "mock_completed",
                "image_path": image_path,
                "faces": [{"name": "Mock_Person", "confidence": 0.95, "bbox": [10, 20, 30, 40]}],
                "analysis_timestamp": datetime.now().isoformat()
            }

    mock_vision_engine = MockVisionEngine(config={"enabled": True})
    ui = VideoUI(mock_vision_engine)
    ui.create_interface().launch(debug=True)
