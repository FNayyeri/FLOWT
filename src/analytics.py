import json
import pandas as pd
from collections import Counter
import numpy as np
<<<<<<< HEAD
import yaml
from pathlib import Path

curated_base_dir = Path("data/curated")
tracking_base_dir = Path("data/tracking")
analysis_base_dir = Path("data/analysis")
=======
>>>>>>> 72b8e1e1f0a7e01f097607743d6e659c209801f9

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
<<<<<<< HEAD
    def get_class_order(self):
        import yaml
        config_path = Path("config/config.yaml")
        if config_path.exists():
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            class_names = config.get('detection_classes', {}).get('names', [])
            class_colors = config.get('detection_classes', {}).get('color_hex', [])
            class_color_map = dict(zip(class_names, class_colors))
        else:
            class_color_map = {}
        class_order = {name: idx for idx, name in enumerate(config.get('detection_classes', {}).get('names', []))}
        return class_order, class_color_map
    def calculate_metrics(self, data, class_order):
        """Calculate performance metrics"""
        if not data:
            return {}
        correct_trash = 0
        misclassified = 0
        not_trash = 0
        metrics = {}
        class_metrics = []
        # D_polystyrene_records = pd.DataFrame(data)[pd.DataFrame(data)["class"]=='D_polystyrene'] ; misclassified_D_polystyrene=0
        for detection in data:
            # video = detection.get('video', '')
            is_true = detection.get('is_true_positive', False)
            original_class = detection.get('class', '')
            corrected_class = detection.get('corrected_class', original_class)
            
            if not is_true:
                not_trash += 1
            elif is_true and original_class != corrected_class:
                misclassified += 1
            
            else:  # is_true and (same class or no correction)
                correct_trash += 1
        
        total_detections = len(data)
        accuracy = (correct_trash / total_detections)*100 if total_detections > 0 else 0
        trash_presence = (correct_trash + misclassified)*100 / total_detections if total_detections > 0 else 0
        classification_acc = correct_trash*100 / (correct_trash + misclassified) if (correct_trash + misclassified) > 0 else 0
        
        df = pd.DataFrame(data)
        valid_trash = df[df['is_true_positive'] == True]

        correct_class_counts = pd.Series()
        misclass_counts = pd.Series()
        no_trash_counts = pd.Series()
                            
        if not valid_trash.empty and 'corrected_class' in valid_trash.columns:
            # Correct trash distribution
            correct_class = valid_trash[(valid_trash['corrected_class'].isna()) | (valid_trash['corrected_class']==valid_trash['class'])]
            correct_class_counts = correct_class['corrected_class'].value_counts(dropna=True)

        misclassified_trash = valid_trash[
            (valid_trash['corrected_class'].notna()) & 
            (valid_trash['class'] != valid_trash['corrected_class'])
        ]
        if not misclassified_trash.empty and 'corrected_class' in misclassified_trash.columns:
            if not misclassified_trash.empty and 'corrected_class' in misclassified_trash.columns:
                misclass_counts = misclassified_trash['corrected_class'].value_counts(dropna=True)

        not_trash_data = df[df['is_true_positive'] == False]
        if not not_trash_data.empty:    
            if not not_trash_data.empty:
                no_trash_counts = not_trash_data['corrected_class'].value_counts(dropna=True)

        all_classes = set(df['corrected_class'].unique())
        # Filter out None values
        all_classes = {cls for cls in all_classes if cls is not None}
        all_classes = sorted(all_classes, key=lambda x: class_order.get(x, float('inf')))
        if 'class' in df.columns:
            
            # for class_name in sorted(all_classes):
            for class_name in all_classes:
                correctly_detected_cls = int(correct_class_counts[class_name]) if class_name in correct_class_counts else 0
                
                misclassified_cls = int(misclass_counts[class_name]) if class_name in misclass_counts else 0
                falsely_detected_cls = int(no_trash_counts[class_name]) if class_name in no_trash_counts else 0
                total_detections_cls = correctly_detected_cls + misclassified_cls + falsely_detected_cls
                accuracy_cls = correctly_detected_cls*100 / total_detections_cls if total_detections_cls > 0 else 0
                trash_precence_cls = (correctly_detected_cls + misclassified_cls)*100 / total_detections_cls if total_detections_cls > 0 else 0 
                classification_acc_cls = correctly_detected_cls*100 / (correctly_detected_cls + misclassified_cls) if (correctly_detected_cls + misclassified_cls) > 0 else 0

                class_metrics.append({
                    'Class': class_name,
                    'Total Detections': total_detections_cls,
                    'Correctly Detected': correctly_detected_cls,
                    'Misclassified': misclassified_cls,
                    'Falsely Detected': falsely_detected_cls,
                    'Average Confidence': f"{df[df['class'] == class_name]['confidence'].mean()*100 if not df[df['class'] == class_name].empty else 0:.2f}",
                    'Accuracy': f"{accuracy_cls:.2f}",
                    'Trash Precence': f"{trash_precence_cls:.2f}",
                    'Classification Accuracy': f"{classification_acc_cls:.2f}"
                })              
        metrics = {
            
            'Total Detections': total_detections,
            'Correctly Detected': correct_trash,
            'Misclassified': misclassified,
            'Falsely Detected': not_trash,
            'Average Confidence': f"{df['confidence'].mean()*100 if not df.empty else 0:.2f}",
            'Accuracy': f"{accuracy:.2f}",
            'Trash Precence': f"{trash_presence:.2f}",
            'Classification Accuracy': f"{classification_acc:.2f}"
        }
        return metrics, class_metrics
        # return class_metrics
    
    def analyse_confidence_distribution(self, data):
        """Analyse confidence score distribution"""
        if not data:
            return {}
        df = pd.DataFrame(data)
        conf_counts = {}
        if 'confidence' in df.columns:
            # Add category column to dataframe
            df_with_outcome = df.copy()
            
            df_with_outcome['Outcome'] = df_with_outcome.apply(
                lambda row: 'Not Trash' if not row.get('is_true_positive', False)
                else ('Misclassified' if pd.notna(row.get('corrected_class')) and row.get('class', '') != row.get('corrected_class', row.get('class', ''))
                else 'Correct Trash'), axis=1)

            # Create confidence bins based on actual data range
            min_conf = df['confidence'].min()
            max_conf = df['confidence'].max()
            
            df_with_outcome['confidence_bin'] = pd.cut(
                df_with_outcome['confidence'], 
                bins=10,
                include_lowest=True
            )
            # Count by category and confidence bin
            conf_counts = df_with_outcome.groupby(['confidence_bin', 'Outcome'], observed=True).size().reset_index(name='count')

            # Convert interval to string for better display
            conf_counts['confidence_range'] = conf_counts['confidence_bin'].apply(
                lambda x: f"{x.left:.2f}-{x.right:.2f}" if pd.notna(x) else 'NaN'
            )

        return conf_counts
    
    def analyse_trackings(self, tracking_data):
        """Analyse tracking data for movement patterns"""
        if not tracking_data:
            return {}
        tracking_metrics = []
        tracking_classes = []
        for tracking in tracking_data:
            video_stats = tracking.get('statistics', {})
            parameters = tracking.get('parameters', {})
            tracked_objects = tracking.get('tracked_objects', [])
            statistics = tracking.get('statistics', {})
            if video_stats:
                video = tracking.get('video', '')
            if parameters:
                timelapse_video = bool(parameters.get('timelapse_video', False)) if parameters.get('timelapse_video') != '' else False
                iou_threshold = float(parameters.get('iou_threshold', '')) if parameters.get('iou_threshold') != '' else np.nan
                template_threshold = float(parameters.get('template_threshold', '')) if parameters.get('template_threshold') != '' else np.nan 
            if statistics:
                total_unique_objects = statistics.get('total_unique_objects', 0)
                total_detections = statistics.get('total_detections', 0)
            
            metrics = {
                'Video': video,
                'Timelapse Video': bool(timelapse_video) if timelapse_video != '' else False,
                'IoU Threshold': float(iou_threshold) if iou_threshold != '' else np.nan,
                'Template Threshold': float(template_threshold) if template_threshold != '' else np.nan,
                'Detections': total_detections,
                'Unique Trash': total_unique_objects
            }
            
            if tracked_objects:
                tracked_objects_df = pd.DataFrame(tracked_objects)
                frames_count = tracked_objects_df.groupby('track_id')['frame'].count().to_dict().values()
                classes = tracked_objects_df['class'].unique()
                detections_by_class = tracked_objects_df['class'].value_counts().to_dict()
                objects_by_class = tracked_objects_df.groupby('class')['track_id'].nunique().to_dict()
                total_unique_objects = len(classes)
                avg_confidences = tracked_objects_df.groupby('class')['confidence'].mean().to_dict()
                min_confidences = tracked_objects_df.groupby('class')['confidence'].min().to_dict()
                max_confidences = tracked_objects_df.groupby('class')['confidence'].max().to_dict()
                
                # Create separate dictionary for each class
                for class_name in classes:
                    tracking_class = {
                        'Video': video,
                        'Timelapse Video': bool(timelapse_video) if timelapse_video != '' else False,
                        'IoU Threshold': float(iou_threshold) if iou_threshold != '' else np.nan,
                        'Template Threshold': float(template_threshold) if iou_threshold != '' else np.nan,
                        'Class': class_name,
                        'Detections': detections_by_class.get(class_name, 0),
                        'Unique Trash': objects_by_class.get(class_name, 0),
                        'Avg Confidence': f"{avg_confidences.get(class_name, 0)*100:.2f}",
                        'Min Confidence': f"{min_confidences.get(class_name, 0)*100:.2f}",
                        'Max Confidence': f"{max_confidences.get(class_name, 0)*100:.2f}"
                    } 
                    tracking_classes.append(tracking_class)
                
            tracking_metrics.append(metrics)
        return tracking_metrics, tracking_classes
    
    def analyse_tags(self, data):
        """Analyze tag usage by class"""
        tag_by_class = {}
        tag_summary = []
        class_tag_combinations = Counter()
        
        for detection in data:
            # Use corrected_class if available, otherwise use class
            class_name = detection.get('corrected_class') or detection.get('class', 'Unknown')
            tags = detection.get('tags', [])
            
            if class_name not in tag_by_class:
                tag_by_class[class_name] = Counter()
            
            if tags:
                tag_by_class[class_name].update(tags)
                # Create class-tag combinations for pie chart
                for tag in tags:
                    class_tag_combinations[f"{class_name} - {tag}"] += 1
        
        # Create summary data for CSV
        for class_name, tag_counter in tag_by_class.items():
            total_class_tags = sum(tag_counter.values())
            for tag, count in tag_counter.items():
                percentage = (count / total_class_tags * 100) if total_class_tags > 0 else 0
                tag_summary.append({
                    'Class': class_name,
                    'Tag': tag,
                    'Count': count,
                    'Percentage_in_Class': f"{percentage:.1f}%"
                })
        
        # Overall tag distribution for pie chart
        all_tags = []
        for detection in data:
            tags = detection.get('tags', [])
            if tags:
                all_tags.extend(tags)
        
        overall_tag_counts = Counter(all_tags)
        
        return {
            'tag_by_class': {k: dict(v) for k, v in tag_by_class.items()},
            'tag_summary': tag_summary,
            'overall_tag_distribution': dict(overall_tag_counts),
            'class_tag_combinations': dict(class_tag_combinations)
        }

    # def generate_detection_report(self, class_order, model_curated_dir, class_metric_csv, selected_video='All'):
    def generate_detection_report(self, class_order, model_curated_dir, selected_video='All'):
        """Generate comprehensive detection analytics report"""
        all_data=[]
        class_metrics_df = pd.DataFrame()
        metrics_df = pd.DataFrame()
        conf_counts = pd.DataFrame()
        class_performance_df = pd.DataFrame()
        tag_analysis = {}
        all_data_videos = {}
        selected_model = model_curated_dir.stem
        model_analysis_dir = analysis_base_dir / selected_model
        model_analysis_dir.mkdir(parents=True, exist_ok=True)

        curated_files = list(model_curated_dir.glob("*_curated_detections.json"))
        
        csv_name = selected_video.replace('.mp4', '') if selected_video.endswith('.mp4') else selected_video
        class_metric_csv = model_analysis_dir / f"detection_performance_{csv_name}.csv"
        if selected_video == "All": 
            for curated_file in curated_files:
                file_data = self.load_curated_data(curated_file)
                filename = curated_file.stem.replace('_curated_detections', '') if curated_file.stem.endswith('_curated_detections') else curated_file.stem.split('_curated_detections')[0]
                if isinstance(file_data, list):
                    for d in file_data:
                        d['video'] = filename + '.mp4'
                if file_data :
                    all_data_videos[filename]= file_data
                    all_data.extend([file_data] if isinstance(file_data, dict) else file_data)
        else:
            selected_video_stem = selected_video.replace('.mp4', '')
            specific_file = model_curated_dir / f"{selected_video_stem}_curated_detections.json"
            if specific_file.exists():
                file_data = self.load_curated_data(specific_file)
                if isinstance(file_data, list):
                    for d in file_data:
                        d['video'] = selected_video
                all_data_videos[selected_video]= file_data
                all_data.extend([file_data] if isinstance(file_data, dict) else file_data)
        if all_data:
            metrics, class_metrics = self.calculate_metrics(all_data, class_order)
            conf_counts = self.analyse_confidence_distribution(all_data)
            tag_analysis = self.analyse_tags(all_data)

            class_metrics_df = pd.DataFrame(class_metrics)
            # Remove rows with NaN or None class names
            class_metrics_df = class_metrics_df.dropna(subset=['Class'])
            class_metrics_df = class_metrics_df[class_metrics_df['Class'] != 'None']
            metrics_df = pd.DataFrame([metrics])

            class_performance_df = class_metrics_df.copy()
            class_performance_df.set_index('Class', inplace=True)

            class_performance_df.to_csv(class_metric_csv, index=True)
            
            # Save tag analysis to CSV
            if tag_analysis['tag_summary']:
                # Save detailed tag analysis by class
                tag_analysis_csv = model_analysis_dir / f"tag_analysis_{csv_name}.csv"
                tag_df = pd.DataFrame(tag_analysis['tag_summary'])
                tag_df.to_csv(tag_analysis_csv, index=False)
                
                # Save overall tag distribution
                if tag_analysis['overall_tag_distribution']:
                    overall_tags_csv = model_analysis_dir / f"overall_tag_distribution_{csv_name}.csv"
                    overall_df = pd.DataFrame(list(tag_analysis['overall_tag_distribution'].items()), 
                                            columns=['Tag', 'Count'])
                    overall_df.to_csv(overall_tags_csv, index=False)
                
                # Save class-tag combinations
                if tag_analysis['class_tag_combinations']:
                    class_tag_csv = model_analysis_dir / f"class_tag_combinations_{csv_name}.csv"
                    class_tag_df = pd.DataFrame(list(tag_analysis['class_tag_combinations'].items()), 
                                               columns=['Class_Tag', 'Count'])
                    class_tag_df.to_csv(class_tag_csv, index=False)
        else:
            # Return empty values if no data
            tag_analysis = {}
        
        return metrics_df, class_metrics_df, class_performance_df, conf_counts, tag_analysis, all_data_videos

    def generate_tracking_report(self, model_tracking_dir, selected_video='All'):
        """Generate comprehensive tracking analytics report"""
        all_tracking_data=[]
        tracking_classes_df = pd.DataFrame()
        tracking_metrics_df = pd.DataFrame()
        selected_model = model_tracking_dir.stem
        model_analysis_dir = analysis_base_dir / selected_model
        model_analysis_dir.mkdir(parents=True, exist_ok=True)
        csv_name = selected_video.replace('.mp4', '') if selected_video.endswith('.mp4') else selected_video

        tracking_classes_all_csv = model_analysis_dir / f"tracking_performance_{csv_name}.csv"

        tracking_files = list(model_tracking_dir.glob("*.json"))

        if selected_video == "All": 
            for tracking_file in tracking_files:
                tracking_data = self.load_curated_data(tracking_file)
                if tracking_data:
                    all_tracking_data.extend([tracking_data] if isinstance(tracking_data, dict) else tracking_data)
        else:
            selected_video_stem = selected_video.replace('.mp4', '')
            specific_file = model_tracking_dir / f"{selected_video_stem}_tracking.json"
            if specific_file.exists():
                tracking_data = self.load_curated_data(specific_file)
                tracking_data['video'] = selected_video
                all_tracking_data.extend([tracking_data] if isinstance(tracking_data, dict) else tracking_data)
        if all_tracking_data:
            tracking_metrics, tracking_classes = self.analyse_trackings(all_tracking_data)

            tracking_classes_df = pd.DataFrame(tracking_classes)
            tracking_metrics_df = pd.DataFrame(tracking_metrics)

        tracking_performance_all_df =tracking_metrics_df.copy()
        tracking_all = pd.DataFrame([{
            'Video': 'Overall',
            'Timelapse Video': tracking_metrics_df['Timelapse Video'].value_counts().get(True, False),
            'IoU Threshold': np.nan,
            'Template Threshold': np.nan,
            'Unique Trash': tracking_metrics_df['Unique Trash'].sum(),
            'Detections': tracking_metrics_df['Detections'].sum()
        }])
        tracking_performance_all_df = pd.concat([tracking_performance_all_df, tracking_all], ignore_index=True)
        
        # Sort the tracking classes dataframe by Video
        tracking_clas_all_df = tracking_classes_df.copy()
        tracking_clas_all_df.sort_values('Video', inplace=True)
        tracking_clas_all= pd.DataFrame([{
            'Video': 'All',
            'Class': 'Overall',
            'Unique Trash': tracking_clas_all_df['Unique Trash'].sum(),
            'Detections': tracking_clas_all_df['Detections'].sum(),
            'Avg Confidence': f"{tracking_clas_all_df['Avg Confidence'].astype(float).mean():.2f}",
            'Min Confidence' : f"{tracking_clas_all_df['Min Confidence'].astype(float).mean():.2f}",
            'Max Confidence' : f"{tracking_clas_all_df['Max Confidence'].astype(float).mean():.2f}"
        }
        ])
        tracking_clas_all_df = pd.concat([tracking_clas_all_df, tracking_clas_all], ignore_index=True)
        tracking_clas_all_df.to_csv(tracking_classes_all_csv, index=False)
        return tracking_performance_all_df, tracking_classes_df, tracking_clas_all_df
    
    def generate_analysis_report(self, class_order, selected_model, selected_video, type='detection'):
        if type == 'detection':
            model_curated_dir = curated_base_dir / selected_model
            self.generate_detection_report(class_order, model_curated_dir, selected_video)
        if type == 'tracking':
            model_tracking_dir = tracking_base_dir / selected_model
            self.generate_tracking_report(model_tracking_dir, selected_video)
    
=======
    
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
>>>>>>> 72b8e1e1f0a7e01f097607743d6e659c209801f9
