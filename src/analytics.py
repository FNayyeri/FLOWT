import json
import pandas as pd
from collections import Counter
import numpy as np

class AnalyticsEngine:
    def __init__(self):
        pass
    
    def load_curated_data(self, curated_file):
        """Load curated detection data"""
        try:
            with open(curated_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return []
    
    def calculate_metrics(self, data):
        """Calculate performance metrics"""
        if not data:
            return {}
        
        df = pd.DataFrame(data)
        
        metrics = {
            'total_detections': len(data),
            'true_positives': df['is_true_positive'].sum() if 'is_true_positive' in df else 0,
            'false_positives': len(data) - (df['is_true_positive'].sum() if 'is_true_positive' in df else 0),
            'accuracy': df['is_true_positive'].mean() if 'is_true_positive' in df else 0,
            'avg_confidence': df['confidence'].mean() if 'confidence' in df else 0,
            'confidence_std': df['confidence'].std() if 'confidence' in df else 0
        }
        
        return metrics
    
    def analyze_class_distribution(self, data):
        """Analyze distribution of detected classes"""
        if not data:
            return {}
        
        classes = [d.get('corrected_class', d.get('class', 'Unknown')) for d in data]
        class_counts = Counter(classes)
        
        return {
            'class_distribution': dict(class_counts),
            'num_unique_classes': len(class_counts),
            'most_common_class': class_counts.most_common(1)[0] if class_counts else None
        }
    
    def analyze_confidence_distribution(self, data):
        """Analyze confidence score distribution"""
        if not data:
            return {}
        
        confidences = [d.get('confidence', 0) for d in data]
        
        return {
            'mean_confidence': np.mean(confidences),
            'median_confidence': np.median(confidences),
            'confidence_quartiles': np.percentile(confidences, [25, 50, 75]).tolist(),
            'low_confidence_count': sum(1 for c in confidences if c < 0.5),
            'high_confidence_count': sum(1 for c in confidences if c > 0.8)
        }
    
    def analyze_tags(self, data):
        """Analyze tag usage"""
        all_tags = []
        for detection in data:
            if 'tags' in detection and detection['tags']:
                all_tags.extend(detection['tags'])
        
        tag_counts = Counter(all_tags)
        
        return {
            'tag_distribution': dict(tag_counts),
            'total_tags': len(all_tags),
            'unique_tags': len(tag_counts),
            'most_common_tags': tag_counts.most_common(5)
        }
    
    def performance_by_class(self, data):
        """Calculate performance metrics by class"""
        if not data:
            return {}
        
        df = pd.DataFrame(data)
        if 'corrected_class' not in df or 'is_true_positive' not in df:
            return {}
        
        class_performance = df.groupby('corrected_class').agg({
            'is_true_positive': ['count', 'sum', 'mean'],
            'confidence': ['mean', 'std']
        }).round(3)
        
        return class_performance.to_dict()
    
    def generate_report(self, data):
        """Generate comprehensive analytics report"""
        report = {
            'summary': self.calculate_metrics(data),
            'class_analysis': self.analyze_class_distribution(data),
            'confidence_analysis': self.analyze_confidence_distribution(data),
            'tag_analysis': self.analyze_tags(data),
            'performance_by_class': self.performance_by_class(data),
            'timestamp': pd.Timestamp.now().isoformat()
        }
        
        return json.dumps(report, indent=2)
    
    def compare_models(self, data_list, model_names):
        """Compare performance across different models"""
        comparison = {}
        
        for i, data in enumerate(data_list):
            model_name = model_names[i] if i < len(model_names) else f"Model_{i+1}"
            comparison[model_name] = self.calculate_metrics(data)
        
        return comparison