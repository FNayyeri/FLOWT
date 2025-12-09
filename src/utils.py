import cv2
import json
from pathlib import Path
from datetime import datetime


def load_video(original_file_path, target_dir):
    """Convert video to MP4 format if not already MP4."""
    file_ext = original_file_path.suffix.lower()
    if file_ext != '.mp4':
        mp4_file_path = target_dir / f"{original_file_path.stem}.mp4"
        
        cap_read = cv2.VideoCapture(str(original_file_path))
        fps = cap_read.get(cv2.CAP_PROP_FPS)
        width = int(cap_read.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap_read.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(str(mp4_file_path), fourcc, fps, (width, height))
        
        while True:
            ret, frame = cap_read.read()
            if not ret:
                break
            out.write(frame)
        
        cap_read.release()
        out.release()
        
        original_file_path.unlink()
        return mp4_file_path
    return original_file_path


def load_image(file_path):
    """Load image using OpenCV."""
    return cv2.imread(str(file_path))


def extract_metadata(file_path, original_filename, is_image=False):
    """Extract metadata from video or image file."""
    file_ext = file_path.suffix.lower()
    file_size = file_path.stat().st_size
    creation_time = datetime.fromtimestamp(file_path.stat().st_ctime)
    
    if is_image:
        img = load_image(file_path)
        height, width = img.shape[:2]
        
        metadata = {
            "filename": file_path.name,
            "original_filename": original_filename,
            "file_size_bytes": file_size,
            "file_size_mb": round(file_size / (1024*1024), 2),
            "file_type": file_ext,
            "media_type": "image",
            "resolution": f"{width}x{height}",
            "width": width,
            "height": height,
            "creation_time": creation_time.isoformat(),
            "ingestion_time": datetime.now().isoformat(),
            "scenario": "marine_litter_detection"
        }
    else:
        cap = cv2.VideoCapture(str(file_path))
        
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        duration = frame_count / fps if fps > 0 else 0
        
        metadata = {
            "filename": file_path.name,
            "original_filename": original_filename,
            "file_size_bytes": file_size,
            "file_size_mb": round(file_size / (1024*1024), 2),
            "file_type": ".mp4",
            "original_format": file_ext,
            "media_type": "video",
            "duration_seconds": round(duration, 2),
            "duration_formatted": f"{int(duration//60):02d}:{int(duration%60):02d}",
            "fps": round(fps, 2),
            "frame_count": frame_count,
            "resolution": f"{width}x{height}",
            "width": width,
            "height": height,
            "creation_time": creation_time.isoformat(),
            "ingestion_time": datetime.now().isoformat(),
            "scenario": "marine_litter_detection",
            "format_details": {
                "codec": "unknown",
                "bitrate": "unknown"
            }
        }
        
        cap.release()
    
    return metadata