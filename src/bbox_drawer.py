import cv2
import numpy as np
import yaml
from pathlib import Path

class BBoxDrawer:
    def __init__(self):
        # Load configuration from config file
        config_path = Path(__file__).parent.parent / "config" / "config.yaml"
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        self.class_names = config['detection_classes']['names']
        self.class_colors_hex = config['detection_classes']['color_hex']
        self.styling = config.get('styling', {})
    
    def get_class_color(self, class_name):
        """Get RGB color for a specific class from hex"""
        hex_color = self.get_class_color_hex(class_name)
        hex_color = hex_color.lstrip('#')
        rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        return rgb
    
    def get_class_color_hex(self, class_name):
        """Get hex color for a specific class"""
        try:
            idx = self.class_names.index(class_name)
            return self.class_colors_hex[idx]
        except ValueError:
            return "#FFFFFF"  # White for unknown classes
    
    def get_class_color_bgr(self, class_name):
        """Get BGR color for OpenCV from hex color"""
        hex_color = self.get_class_color_hex(class_name)
        # Convert hex to RGB then to BGR for OpenCV
        hex_color = hex_color.lstrip('#')
        rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        bgr = (rgb[2], rgb[1], rgb[0])  # Convert RGB to BGR
        return bgr
    
    def draw_bbox(self, frame, bbox, class_name, confidence=None, track_id=None, show_label=False, thickness=None, text_color=None):
        """Draw bounding box with class-specific color"""
        x1, y1, x2, y2 = map(int, bbox)
        color = self.get_class_color_bgr(class_name)
        
        # Use config values if not provided
        if thickness is None:
            thickness = self.styling.get('bbox', {}).get('thickness', 2)
        if text_color is None:
            text_color = tuple(self.styling.get('bbox', {}).get('text_color', [255, 255, 255]))
        
        font_scale = self.styling.get('bbox', {}).get('font_scale', 0.6)
        text_thickness = self.styling.get('bbox', {}).get('text_thickness', 1)
        
        # Draw bounding box
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, thickness)
        
        # Draw label only if requested
        if show_label:
            label_parts = []
            # Only add class name if show_labels is enabled (passed via show_label)
            label_parts.append(class_name)
            if track_id is not None:
                label_parts.append(f"ID:{track_id}")
            if confidence is not None:
                label_parts.append(f"{confidence:.2f}")
            
            label = " ".join(label_parts)
            (text_width, text_height), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, font_scale, text_thickness)
            cv2.rectangle(frame, (x1, y1 - text_height - 10), (x1 + text_width, y1), color, -1)
            cv2.putText(frame, label, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, font_scale, text_color, text_thickness)
        
        return frame
    
    def draw_bbox_with_options(self, frame, bbox, class_name, confidence, track_id, show_any_label, thickness, text_color, custom_color=None):
        """Draw bounding box with specific display options"""
        x1, y1, x2, y2 = map(int, bbox)
        
        # Use custom color if provided, otherwise use class color
        if custom_color:
            color = custom_color
            # print(f"DEBUG: BBoxDrawer using custom color {custom_color}")
        elif class_name:
            color = self.get_class_color_bgr(class_name)
            # print(f"DEBUG: BBoxDrawer using class color {color} for {class_name}")
        else:
            color = (255, 255, 255)  # Default white
            # print(f"DEBUG: BBoxDrawer using default white color")
        
        # Use config values if not provided
        if thickness is None:
            thickness = self.styling.get('bbox', {}).get('thickness', 2)
        if text_color is None:
            text_color = tuple(self.styling.get('bbox', {}).get('text_color', [255, 255, 255]))
        
        font_scale = self.styling.get('bbox', {}).get('font_scale', 0.6)
        text_thickness = self.styling.get('bbox', {}).get('text_thickness', 1)
        
        # Draw bounding box
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, thickness)
        
        # Draw label only if requested and components exist
        if show_any_label:
            label_parts = []
            if class_name:
                label_parts.append(class_name)
            if track_id is not None:
                label_parts.append(f"ID:{track_id}")
            if confidence is not None:
                label_parts.append(f"{confidence:.2f}")
            
            if label_parts:  # Only draw if there are parts to show
                label = " ".join(label_parts)
                (text_width, text_height), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, font_scale, text_thickness)
                cv2.rectangle(frame, (x1, y1 - text_height - 10), (x1 + text_width, y1), color, -1)
                cv2.putText(frame, label, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, font_scale, text_color, text_thickness)
        
        return frame