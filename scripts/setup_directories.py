import os
import json

def setup_directories():
    """Creates all necessary directories for JARVIS AI."""
    directories = [
        "data",
        "data/chroma_db",
        "data/vision_cache", 
        "data/ethical_violations",
        "data/feedback_logs",
        "data/scraping_logs",
        "data/self_correction_log",
        "data/video_datasets",
        "logs"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✓ Created directory: {directory}")
    
    # Create metadata.json if it doesn't exist
    metadata_file = "data/video_datasets/metadata.json"
    if not os.path.exists(metadata_file):
        metadata = {
            "dataset_name": "Placeholder Video Dataset",
            "description": "This is a placeholder metadata file. Add your video details here.",
            "version": "1.0",
            "created_date": "2023-10-26T10:00:00Z",
            "videos": []
        }
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        print(f"✓ Created metadata file: {metadata_file}")

if __name__ == "__main__":
    setup_directories()
    print("\n🎉 All directories set up successfully!")
