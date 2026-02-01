# Aperture-Labs-Project
CSCI 577A Spring 2026 Group Project

## VLM Architectures for Defect Detection

### 1. Contrastive (CLIP, SigLIP)
- Dual encoder, shared embedding space
- Zero-shot classification only
- Fast, no localization

### 2. Open-Vocab Detection (OWLv2)
- Text-conditioned object detection
- Bounding box output
- No retraining for new defect types

### 3. Generative VLM (Florence-2, PaliGemma)
- Image → LLM → natural language output
- Flexible QA, descriptions
- Slower, may hallucinate

### 4. Region-Based (GLIP)
- Region proposals → VLM reasoning per region
- Good for multi-defect scenes
- Two-stage latency

### 5. Segmentation VLM (CLIPSeg, SAM hybrids)
- Pixel-level masks from text
- Precise boundaries
- Slower, still maturing

### 6. Seq2Seq (Florence-2, Pix2Seq)
- Unified detection + captioning + VQA
- Structured outputs
- Single model, multiple tasks

### 7. Anomaly + VLM (WinCLIP, AnomalyCLIP)
- Learns "normal," flags deviations
- No defect labels needed
- Sensitive to training distribution

### 8. Hybrid Pipelines
- Chain: Detector → Segmenter → Classifier → LLM
- Best-in-class per stage
- Complex, higher latency

# What are we going to use?
Not sure yet. Still looking it up
## Encoder-Based: Easiest
**CLIP** (Constrastive Language Image Pre-Training): 
* Dual encoders (vision and test). 
    * Learns from being trained on (image, text) pairs, which allows it to perform zero-shot classification. 
* Zero Shot = Classify new examples from previously unseen classes.

