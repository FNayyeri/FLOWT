## Flowt Pipeline - Core Features

### 1. **📁 Data Ingestion - Video Upload**
- Supports multiple video formats: `.MP4`, `.AVI`, `.MOV`, `.MKV`, `.TLS`.
- Ingestion supports both normal and timelapse videos for flexible use cases.
- Metadata extraction on upload (duration, resolution, file size, creation time).
- Consistent `.mp4` display format for user-facing select boxes, regardless of actual underlying format.
- Timelapse videos can be explicitly marked during tracking to adjust processing parameters (e.g., disable IoU threshold).

### 2. **🔍 Scanning Tool**
- Model Selection: Support for both base models and fine-tuned models with automatic sorting by modification time
- Machine Learning Integration: Real-time object detection with configurable confidence thresholds
- File Overwrite Protection: Warning system when scanning would overwrite existing detection, curated, tracking, or analysis files
- Results Display: Detection results table

### 4. **✏️ Review Tool**
- Manual Review: Page-by-page review of detection results with customisable pagination
- True/False Positive Marking: Individual and bulk operations (scoped to current page)
- Classification Correction: Edit detected classes with dropdown selection
- Tagging System: Add custom tags to detections for better organisation and further analysis

### 5. **🎯 Tracking Tool**
- Advanced Techniques: IoU and template matching for object tracking across video frames
- Timelapse Support: Special mode for timelapse videos with disabled IoU threshold
- Configurable Parameters: Adjustable IoU and template matching thresholds
- Performance Statistics: Comprehensive tracking metrics and success rates

### 6. **🎬 Video Generation**
- Annotated Videos: Generate videos with corrected detections overlaid
- Customisable Appearance: Configurable text colors, bounding box colors and thickness
- Multiple Formats: Output support for MP4, AVI, MOV formats
- Quality Control: Selectable video quality levels (High, Medium, Low)

### 7. **📊 Analysis Pages**
- **Trash Analysis**:
   - Detection Analytics: Comprehensive performance metrics including accuracy, precision, recall
   - Class Distribution: Visual analysis of detected object classes with pie charts and histograms
   - Confidence Analysis: Distribution analysis of detection confidence scores
   - Tag Analytics: Frequency analysis of custom tags
   - Video-Specific Analysis: Option to analyse all videos or focus on specific ones

- **AI Insight**:
   - LLM Integration: Support for intelligent analysis using **OpenAI**
   - Multiple Analysis Types: Performance analysis, trend identification, recommendations, and custom queries
   - Data Integration: Automatic loading of curated detection data with tracking information
   - API Key Management: Secure handling of API credentials with graceful fallbacks

### **🔧Iterative Model Improvement Workflow**
- Iterative Training: Version-controlled model refinement with timestamp-based model naming
- Dataset Management: Automatic dataset creation with duplicate prevention using MD5 hashing
- Performance Monitoring: False positive rate tracking and training specifications logging
- System Integration: GPU information capture and training duration tracking
- Model Lifecycle: Automatic model availability in inference after fine-tuning completion

1. **Upload Reviewed data** through the curation page.
2. **Create a learning dataset**:
   - Prevents duplicates using MD5 hashing.
   - Sequential file naming (`img_000001.jpg`, etc.).
3. **Run training**:
   - Uses the most recent model as a baseline.
   - Logs GPU info, system specs, and training duration.
4. **Evaluate performance** using false positive monitoring.
5. **Deploy new model** for immediate use in inference.
