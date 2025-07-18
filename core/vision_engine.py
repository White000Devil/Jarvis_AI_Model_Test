import cv2
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from utils.logger import logger
import os
import json
import time
from PIL import Image
import base64
import io

class VisionEngine:
    """
    Computer Vision engine for JARVIS AI.
    Handles image processing, object detection, OCR, and video analysis.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.enabled = config.get("enabled", True)
        self.models = config.get("models", {})
        self.cache_path = config.get("cache_path", "data/vision_cache")
        self.max_cache_size_mb = config.get("max_cache_size_mb", 500)
        
        # Ensure cache directory exists
        os.makedirs(self.cache_path, exist_ok=True)
        
        # Initialize model placeholders
        self.object_detector = None
        self.ocr_engine = None
        self.face_recognizer = None
        
        logger.info(f"Vision Engine initialized. Enabled: {self.enabled}")
    
    async def initialize_models(self):
        """Initialize computer vision models."""
        if not self.enabled:
            logger.info("Vision Engine is disabled")
            return
        
        try:
            logger.info("Initializing vision models...")
            
            # Initialize object detection (mock implementation)
            self.object_detector = MockObjectDetector()
            
            # Initialize OCR (mock implementation)
            self.ocr_engine = MockOCREngine()
            
            # Initialize face recognition (mock implementation)
            self.face_recognizer = MockFaceRecognizer()
            
            logger.info("Vision models initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize vision models: {e}")
            self.enabled = False
    
    async def analyze_image(self, image_data: bytes, analysis_type: str = "full") -> Dict[str, Any]:
        """
        Analyze an image and extract information.
        
        Args:
            image_data: Raw image bytes
            analysis_type: Type of analysis (full, objects, text, faces)
            
        Returns:
            Dictionary containing analysis results
        """
        if not self.enabled:
            return {"error": "Vision Engine is disabled", "status": "disabled"}
        
        try:
            # Convert bytes to OpenCV image
            nparr = np.frombuffer(image_data, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if image is None:
                return {"error": "Invalid image data", "status": "error"}
            
            results = {
                "status": "success",
                "image_info": {
                    "width": image.shape[1],
                    "height": image.shape[0],
                    "channels": image.shape[2] if len(image.shape) > 2 else 1
                },
                "timestamp": time.time()
            }
            
            # Perform different types of analysis
            if analysis_type in ["full", "objects"]:
                objects = await self._detect_objects(image)
                results["objects"] = objects
            
            if analysis_type in ["full", "text"]:
                text = await self._extract_text(image)
                results["text"] = text
            
            if analysis_type in ["full", "faces"]:
                faces = await self._detect_faces(image)
                results["faces"] = faces
            
            # Generate description
            results["description"] = self._generate_image_description(results)
            
            return results
            
        except Exception as e:
            logger.error(f"Error analyzing image: {e}")
            return {"error": str(e), "status": "error"}
    
    async def analyze_video(self, video_path: str, frame_interval: int = 30) -> Dict[str, Any]:
        """
        Analyze a video file and extract information.
        
        Args:
            video_path: Path to video file
            frame_interval: Analyze every N frames
            
        Returns:
            Dictionary containing video analysis results
        """
        if not self.enabled:
            return {"error": "Vision Engine is disabled", "status": "disabled"}
        
        if not os.path.exists(video_path):
            return {"error": "Video file not found", "status": "error"}
        
        try:
            cap = cv2.VideoCapture(video_path)
            
            if not cap.isOpened():
                return {"error": "Cannot open video file", "status": "error"}
            
            # Get video properties
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            duration = frame_count / fps if fps > 0 else 0
            
            results = {
                "status": "success",
                "video_info": {
                    "fps": fps,
                    "frame_count": frame_count,
                    "duration_seconds": duration,
                    "width": int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
                    "height": int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                },
                "frames_analyzed": [],
                "summary": {},
                "timestamp": time.time()
            }
            
            frame_number = 0
            analyzed_frames = 0
            
            while cap.isOpened() and analyzed_frames < 10:  # Limit to 10 frames for demo
                ret, frame = cap.read()
                if not ret:
                    break
                
                if frame_number % frame_interval == 0:
                    # Analyze this frame
                    frame_analysis = await self._analyze_frame(frame, frame_number)
                    results["frames_analyzed"].append(frame_analysis)
                    analyzed_frames += 1
                
                frame_number += 1
            
            cap.release()
            
            # Generate video summary
            results["summary"] = self._generate_video_summary(results["frames_analyzed"])
            
            return results
            
        except Exception as e:
            logger.error(f"Error analyzing video: {e}")
            return {"error": str(e), "status": "error"}
    
    async def _detect_objects(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """Detect objects in an image."""
        if self.object_detector:
            return await self.object_detector.detect(image)
        
        # Mock object detection
        return [
            {
                "class": "person",
                "confidence": 0.85,
                "bbox": [100, 100, 200, 300]
            },
            {
                "class": "computer",
                "confidence": 0.72,
                "bbox": [300, 150, 500, 400]
            }
        ]
    
    async def _extract_text(self, image: np.ndarray) -> Dict[str, Any]:
        """Extract text from an image using OCR."""
        if self.ocr_engine:
            return await self.ocr_engine.extract_text(image)
        
        # Mock OCR
        return {
            "text": "Sample text extracted from image",
            "confidence": 0.78,
            "language": "en",
            "words": [
                {"text": "Sample", "confidence": 0.85, "bbox": [10, 10, 60, 30]},
                {"text": "text", "confidence": 0.82, "bbox": [70, 10, 100, 30]},
                {"text": "extracted", "confidence": 0.75, "bbox": [110, 10, 180, 30]},
                {"text": "from", "confidence": 0.88, "bbox": [190, 10, 220, 30]},
                {"text": "image", "confidence": 0.79, "bbox": [230, 10, 280, 30]}
            ]
        }
    
    async def _detect_faces(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """Detect faces in an image."""
        if self.face_recognizer:
            return await self.face_recognizer.detect_faces(image)
        
        # Mock face detection
        return [
            {
                "bbox": [150, 50, 250, 150],
                "confidence": 0.92,
                "landmarks": {
                    "left_eye": [170, 80],
                    "right_eye": [230, 80],
                    "nose": [200, 100],
                    "mouth": [200, 120]
                },
                "attributes": {
                    "age": "25-35",
                    "gender": "unknown",
                    "emotion": "neutral"
                }
            }
        ]
    
    async def _analyze_frame(self, frame: np.ndarray, frame_number: int) -> Dict[str, Any]:
        """Analyze a single video frame."""
        # Convert frame to bytes for analysis
        _, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()
        
        # Analyze the frame
        analysis = await self.analyze_image(frame_bytes, "full")
        analysis["frame_number"] = frame_number
        
        return analysis
    
    def _generate_image_description(self, analysis_results: Dict[str, Any]) -> str:
        """Generate a natural language description of the image."""
        description_parts = []
        
        # Describe image dimensions
        info = analysis_results.get("image_info", {})
        description_parts.append(f"Image is {info.get('width', 'unknown')}x{info.get('height', 'unknown')} pixels")
        
        # Describe objects
        objects = analysis_results.get("objects", [])
        if objects:
            object_names = [obj["class"] for obj in objects]
            unique_objects = list(set(object_names))
            if len(unique_objects) == 1:
                description_parts.append(f"Contains {len(objects)} {unique_objects[0]}{'s' if len(objects) > 1 else ''}")
            else:
                description_parts.append(f"Contains {len(objects)} objects including {', '.join(unique_objects[:3])}")
        
        # Describe text
        text_data = analysis_results.get("text", {})
        if text_data and text_data.get("text"):
            word_count = len(text_data.get("words", []))
            description_parts.append(f"Contains {word_count} words of text")
        
        # Describe faces
        faces = analysis_results.get("faces", [])
        if faces:
            description_parts.append(f"Contains {len(faces)} face{'s' if len(faces) > 1 else ''}")
        
        return ". ".join(description_parts) + "."
    
    def _generate_video_summary(self, frame_analyses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate a summary of video analysis."""
        if not frame_analyses:
            return {"description": "No frames analyzed"}
        
        # Count objects across all frames
        all_objects = []
        all_text = []
        face_count = 0
        
        for frame in frame_analyses:
            if "objects" in frame:
                all_objects.extend([obj["class"] for obj in frame["objects"]])
            if "text" in frame and frame["text"].get("text"):
                all_text.append(frame["text"]["text"])
            if "faces" in frame:
                face_count += len(frame["faces"])
        
        unique_objects = list(set(all_objects))
        
        summary = {
            "frames_analyzed": len(frame_analyses),
            "unique_objects": unique_objects,
            "total_objects": len(all_objects),
            "text_instances": len(all_text),
            "total_faces": face_count,
            "description": f"Video analysis of {len(frame_analyses)} frames found {len(unique_objects)} types of objects and {face_count} faces"
        }
        
        return summary
    
    def clear_cache(self):
        """Clear the vision cache directory."""
        try:
            import shutil
            if os.path.exists(self.cache_path):
                shutil.rmtree(self.cache_path)
                os.makedirs(self.cache_path, exist_ok=True)
            logger.info("Vision cache cleared")
        except Exception as e:
            logger.error(f"Error clearing vision cache: {e}")

# Mock implementations for demonstration
class MockObjectDetector:
    """Mock object detector for demonstration purposes."""
    
    async def detect(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """Mock object detection."""
        await asyncio.sleep(0.1)  # Simulate processing time
        
        # Generate mock detections based on image properties
        height, width = image.shape[:2]
        
        detections = []
        
        # Add some random mock detections
        import random
        classes = ["person", "car", "computer", "phone", "book", "chair", "table"]
        
        for i in range(random.randint(1, 4)):
            x1 = random.randint(0, width // 2)
            y1 = random.randint(0, height // 2)
            x2 = random.randint(x1 + 50, min(x1 + 200, width))
            y2 = random.randint(y1 + 50, min(y1 + 200, height))
            
            detections.append({
                "class": random.choice(classes),
                "confidence": random.uniform(0.6, 0.95),
                "bbox": [x1, y1, x2, y2]
            })
        
        return detections

class MockOCREngine:
    """Mock OCR engine for demonstration purposes."""
    
    async def extract_text(self, image: np.ndarray) -> Dict[str, Any]:
        """Mock text extraction."""
        await asyncio.sleep(0.2)  # Simulate processing time
        
        # Generate mock text based on image properties
        sample_texts = [
            "Welcome to JARVIS AI",
            "Computer Vision Demo",
            "Text Recognition Active",
            "Processing Image Data",
            "Machine Learning in Action"
        ]
        
        import random
        selected_text = random.choice(sample_texts)
        words = selected_text.split()
        
        word_data = []
        x_pos = 10
        for word in words:
            word_data.append({
                "text": word,
                "confidence": random.uniform(0.7, 0.95),
                "bbox": [x_pos, 10, x_pos + len(word) * 10, 30]
            })
            x_pos += len(word) * 12
        
        return {
            "text": selected_text,
            "confidence": random.uniform(0.75, 0.9),
            "language": "en",
            "words": word_data
        }

class MockFaceRecognizer:
    """Mock face recognizer for demonstration purposes."""
    
    async def detect_faces(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """Mock face detection."""
        await asyncio.sleep(0.15)  # Simulate processing time
        
        height, width = image.shape[:2]
        faces = []
        
        import random
        num_faces = random.randint(0, 2)
        
        for i in range(num_faces):
            # Generate random face bbox
            face_size = random.randint(80, 150)
            x1 = random.randint(0, max(1, width - face_size))
            y1 = random.randint(0, max(1, height - face_size))
            x2 = min(x1 + face_size, width)
            y2 = min(y1 + face_size, height)
            
            # Generate landmarks
            center_x = (x1 + x2) // 2
            center_y = (y1 + y2) // 2
            
            faces.append({
                "bbox": [x1, y1, x2, y2],
                "confidence": random.uniform(0.8, 0.98),
                "landmarks": {
                    "left_eye": [center_x - 20, center_y - 10],
                    "right_eye": [center_x + 20, center_y - 10],
                    "nose": [center_x, center_y],
                    "mouth": [center_x, center_y + 20]
                },
                "attributes": {
                    "age": random.choice(["18-25", "25-35", "35-45", "45-55", "55+"]),
                    "gender": random.choice(["male", "female", "unknown"]),
                    "emotion": random.choice(["happy", "neutral", "sad", "surprised", "angry"])
                }
            })
        
        return faces

# Test function for Vision Engine
async def test_vision_engine():
    """Test the Vision Engine functionality."""
    logger.info("--- Testing Vision Engine ---")
    
    config = {
        "enabled": True,
        "models": {
            "object_detection": "yolov8n",
            "ocr": "tesseract",
            "face_recognition": "face_recognition"
        },
        "cache_path": "data/vision_cache",
        "max_cache_size_mb": 500
    }
    
    vision_engine = VisionEngine(config)
    await vision_engine.initialize_models()
    
    # Create a test image
    test_image = np.zeros((400, 600, 3), dtype=np.uint8)
    test_image[:] = (100, 150, 200)  # Fill with a color
    
    # Add some shapes to make it interesting
    cv2.rectangle(test_image, (50, 50), (200, 150), (255, 255, 255), -1)
    cv2.circle(test_image, (400, 200), 50, (0, 255, 0), -1)
    cv2.putText(test_image, "JARVIS AI TEST", (100, 300), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    
    # Convert to bytes
    _, buffer = cv2.imencode('.jpg', test_image)
    image_bytes = buffer.tobytes()
    
    # Test image analysis
    logger.info("Testing image analysis...")
    result = await vision_engine.analyze_image(image_bytes, "full")
    
    logger.info(f"Analysis Status: {result['status']}")
    logger.info(f"Image Info: {result.get('image_info', {})}")
    logger.info(f"Objects Found: {len(result.get('objects', []))}")
    logger.info(f"Text Found: {result.get('text', {}).get('text', 'None')}")
    logger.info(f"Faces Found: {len(result.get('faces', []))}")
    logger.info(f"Description: {result.get('description', 'None')}")
    
    logger.info("Vision Engine tests completed successfully!")

if __name__ == "__main__":
    import asyncio
    from utils.logger import setup_logging
    
    setup_logging(debug=True)
    asyncio.run(test_vision_engine())
