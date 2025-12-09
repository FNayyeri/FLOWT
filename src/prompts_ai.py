class PromptsAI:
    @staticmethod
    def short_prompts():
        """Short prompts under ~300 tokens each"""
        return [
            # Data Summary & Insights (~300 tokens)
            """Project: FLOWT Pipeline - Marine litter detection system.
                Analyse this data and provide key insights:
                Metadata: {metadata_summary}
                Detection Summary: {detection_summary}
                Detection Details: {detection_details}
                Tags: {tag_details_summary}
                Classes: {trash_categories_info}
                Focus on main trends and environmental impact.""",
            
            # Performance Analysis (~300 tokens)
            """Project: FLOWT Pipeline - Marine litter detection system.
            Evaluate system performance:
            Metadata: {metadata_summary}
            Confidence: {confidence_summary}
            Detection Details: {detection_details}
            Tags: {tag_details_summary}
            Tracking: {tracking_details}
            Focus on accuracy and improvement areas.""",
            
            # Class Distribution Analysis (~300 tokens)
            """Project: FLOWT Pipeline - Marine litter detection system.
            Analyze class distribution:
            Metadata: {metadata_summary}
            Detection Summary: {detection_summary}
            Detection Details: {detection_details}
            Tags: {tag_details_summary}
            Classes: {trash_categories_info}
            Focus on material composition and environmental impact.""",
            
            # Quality Assessment (~300 tokens)
            """Project: FLOWT Pipeline - Marine litter detection system.
            Assess data quality:
            Metadata: {metadata_summary}
            Confidence: {confidence_summary}
            Detection Details: {detection_details}
            Tags: {tag_details_summary}
            Tracking: {tracking_details}
            Focus on accuracy, confidence levels, and completeness."""
        ]
    
    @staticmethod
    def long_prompts():
        """Long prompts with specified token ranges"""
        return [
            # Data Summary & Insights (800-1200 tokens)
            """Project: FLOWT Pipeline - Floating Litter Observation & Waste Tracking
                Purpose: Automated detection of plastic and floating debris in waterways using computer vision and AI to protect aquatic ecosystems, marine life, and human health.
                ANALYSIS TASK: Comprehensive Data Summary & Environmental Insights
                    VIDEO METADATA: {metadata_summary}
                    DETECTION PERFORMANCE OVERVIEW: {detection_summary}
                    DETAILED CLASS-WISE DETECTION RESULTS: {detection_details}
                    USER-DEFINED TAGS AND ANNOTATIONS: {tag_details_summary}
                    TRASH CATEGORIES AND MATERIAL COMPOSITION: {trash_categories_info}

                ANALYSIS REQUIREMENTS:
                1. Summarise key detection patterns and trends across all processed videos
                2. Identify the most prevalent litter types and their environmental significance
                3. Analyse material composition patterns (plastic vs. metal vs. organic materials)
                4. Assess the environmental impact potential of detected litter categories
                5. Highlight any concerning trends in litter distribution or concentration
                6. Provide insights on seasonal or temporal patterns if evident
                7. Recommend priority areas for cleanup or intervention based on findings
                8. Discuss the ecological implications of the detected litter types
                9. Evaluate the effectiveness of current detection coverage
                10. Suggest improvements for future monitoring campaigns

                Focus on actionable environmental insights that can inform marine conservation efforts and policy decisions.""",
            
            # Performance Analysis (900-1300 tokens)
            """Project: FLOWT Pipeline - Floating Litter Observation & Waste Tracking
                Purpose: Automated detection of plastic and floating debris in waterways using computer vision and AI to protect aquatic ecosystems, marine life, and human health.
                ANALYSIS TASK: Comprehensive Performance Evaluation & System Optimisation
                    VIDEO METADATA AND PROCESSING PARAMETERS: {metadata_summary}
                    CONFIDENCE SCORE ANALYSIS: {confidence_summary}
                    DETAILED DETECTION PERFORMANCE BY CLASS: {detection_details}
                    USER VALIDATION AND TAGGING DATA: {tag_details_summary}
                    OBJECT TRACKING PERFORMANCE: {tracking_details}

                PERFORMANCE EVALUATION REQUIREMENTS:
                1. Analyse overall system accuracy across all 26 litter categories
                2. Identify classes with highest and lowest detection performance
                3. Evaluate confidence score distributions and their correlation with accuracy
                4. Assess false positive and false negative patterns by material type
                5. Analyse tracking consistency and object persistence across frames
                6. Identify potential bias in detection performance across different environmental conditions
                7. Evaluate the impact of video quality parameters (resolution, fps, codec) on detection accuracy
                8. Assess user correction patterns to identify systematic classification errors
                9. Analyse performance variations across different video sources or conditions
                10. Identify classes that are frequently confused with each other
                11. Evaluate the effectiveness of confidence thresholds for different material types
                12. Assess tracking performance for different object sizes and movement patterns
                13. Identify technical limitations and recommend system improvements
                14. Suggest optimal confidence thresholds for different use cases
                15. Recommend training data augmentation strategies based on performance gaps

                Provide specific, actionable recommendations for improving detection accuracy, reducing false positives, and enhancing overall system reliability.""",
            
            # Class Distribution Analysis (800-1100 tokens)
            """Project: FLOWT Pipeline - Floating Litter Observation & Waste Tracking
                Purpose: Automated detection of plastic and floating debris in waterways using computer vision and AI to protect aquatic ecosystems, marine life, and human health.
                ANALYSIS TASK: Marine Litter Class Distribution & Environmental Impact Assessment
                    VIDEO PROCESSING METADATA: {metadata_summary}
                    DETECTION SUMMARY STATISTICS: {detection_summary}
                    CLASS-SPECIFIC DETECTION BREAKDOWN: {detection_details}
                    TAGGING AND ANNOTATION PATTERNS: {tag_details_summary}
                    COMPREHENSIVE LITTER CATEGORY DEFINITIONS: {trash_categories_info}

                CLASS DISTRIBUTION ANALYSIS REQUIREMENTS:
                1. Analyze the relative abundance of each of the 26 litter categories
                2. Group findings by material type (plastic, metal, glass, organic, etc.)
                3. Identify the most environmentally persistent litter types detected
                4. Assess the potential marine life impact of each detected category
                5. Analyze size distribution patterns (small vs. large debris)
                6. Evaluate the presence of microplastics indicators vs. macroplastics
                7. Identify packaging-related litter patterns and their sources
                8. Assess the prevalence of single-use items vs. durable goods
                9. Analyze seasonal or temporal variations in litter composition
                10. Evaluate the effectiveness of current waste management policies based on detected categories
                11. Identify litter types that pose the highest risk to marine ecosystems
                12. Assess the potential for biodegradation vs. persistence of detected materials
                13. Analyze correlation between litter types and potential pollution sources
                14. Evaluate the representation of different consumer product categories
                15. Recommend targeted intervention strategies based on class distribution

                Focus on environmental implications, pollution source identification, and evidence-based recommendations for marine conservation and waste reduction policies.""",
            
            # Quality Assessment (850-1150 tokens)
            """Project: FLOWT Pipeline - Floating Litter Observation & Waste Tracking
                Purpose: Automated detection of plastic and floating debris in waterways using computer vision and AI to protect aquatic ecosystems, marine life, and human health.
                ANALYSIS TASK: Comprehensive Data Quality Assessment & Validation Analysis
                    VIDEO TECHNICAL SPECIFICATIONS: {metadata_summary}
                    CONFIDENCE SCORE DISTRIBUTIONS: {confidence_summary}
                    DETECTION ACCURACY BY CLASS: {detection_details}
                    USER VALIDATION AND CORRECTION PATTERNS: {tag_details_summary}
                    TRACKING QUALITY METRICS: {tracking_details}

                DATA QUALITY ASSESSMENT REQUIREMENTS:
                1. Evaluate overall data completeness across all 26 litter categories
                2. Assess confidence score reliability and calibration accuracy
                3. Analyze the consistency of user annotations and corrections
                4. Evaluate detection consistency across different video quality parameters
                5. Assess the reliability of tracking data and object persistence
                6. Identify potential data quality issues or systematic biases
                7. Evaluate the adequacy of training data representation
                8. Assess inter-annotator agreement where multiple validations exist
                9. Analyze the impact of environmental conditions on data quality
                10. Evaluate temporal consistency in detection performance
                11. Assess the quality of bounding box annotations and spatial accuracy
                12. Identify classes with insufficient training or validation data
                13. Evaluate the effectiveness of quality control measures
                14. Assess data balance across different litter categories and materials
                15. Identify potential overfitting or underfitting issues in model performance
                16. Evaluate the robustness of detections across different lighting and weather conditions
                17. Assess the quality of metadata extraction and technical parameter accuracy
                18. Recommend data collection improvements and quality assurance protocols

                Provide specific recommendations for improving data quality, validation processes, and overall system reliability for marine litter monitoring applications."""
        ]
    
    @staticmethod
    def get_token_info():
        """Return token information for each prompt type"""
        return {
            "short": {
                "Data Summary & Insights": "~300 tokens",
                "Performance Analysis": "~300 tokens", 
                "Class Distribution Analysis": "~300 tokens",
                "Quality Assessment": "~300 tokens"
            },
            "long": {
                "Data Summary & Insights": "800-1200 tokens",
                "Performance Analysis": "900-1300 tokens",
                "Class Distribution Analysis": "800-1100 tokens", 
                "Quality Assessment": "850-1150 tokens"
            }
        }