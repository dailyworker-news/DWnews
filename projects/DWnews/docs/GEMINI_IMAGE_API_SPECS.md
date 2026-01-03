# Google Gemini 2.5 Flash Image API - Technical Specification

**Document Version:** 1.0
**Date:** 2026-01-02
**Project:** The Daily Worker (DWnews)
**Purpose:** Technical specifications for Gemini 2.5 Flash Image integration using google-genai SDK

---

## Overview

Gemini 2.5 Flash Image is Google's latest image generation model, offering superior quality and simplified integration compared to Vertex AI Imagen. This document provides complete technical specifications for implementing Gemini 2.5 Flash Image generation in The Daily Worker platform.

**Key Advantages over Vertex AI Imagen:**
- Simpler SDK (`google-genai` vs. heavyweight `google-cloud-aiplatform`)
- Better image quality with improved prompt adherence
- Faster generation times (10-15s vs. 20-30s)
- More intuitive API with cleaner request/response format
- Production-proven in a-team project with excellent results

---

## SDK Requirements

### Package Installation

```bash
# Install google-genai SDK
pip install google-genai

# Remove old Vertex AI SDK (if present)
pip uninstall google-cloud-aiplatform
```

### Requirements.txt Update

```txt
# Image Generation (NEW - Gemini 2.5 Flash Image)
google-genai>=1.0.0

# Remove these deprecated packages:
# google-cloud-aiplatform>=1.38.0  # DEPRECATED - use google-genai instead
```

---

## API Configuration

### Authentication

**API Key Method (Recommended for MVP):**
```python
import google.generativeai as genai

# Configure with API key
genai.configure(api_key="YOUR_GEMINI_API_KEY")
```

**Environment Variable:**
```bash
export GEMINI_API_KEY="your_api_key_here"
```

**Get API Key:**
- Console: https://aistudio.google.com/apikey
- Project: Must enable Gemini API in Google Cloud Console
- Free tier: 60 requests/minute, 1500 requests/day

---

## API Endpoints & Models

### Model Name

```python
model_name = "gemini-2.5-flash-image"
```

### Available Models (as of 2026-01-02)

| Model | Purpose | Speed | Quality | Cost |
|-------|---------|-------|---------|------|
| `gemini-2.5-flash-image` | Fast image generation | Fast (10-15s) | High | $0.02-0.04/image |
| `gemini-2.5-pro-image` | High-quality generation | Slower (30-40s) | Very High | $0.10-0.15/image |

**Recommendation:** Use `gemini-2.5-flash-image` for MVP (excellent quality/cost ratio)

---

## Request Format

### Basic Image Generation

```python
import google.generativeai as genai

# Configure API
genai.configure(api_key=GEMINI_API_KEY)

# Initialize model
model = genai.GenerativeModel('gemini-2.5-flash-image')

# Generate image
response = model.generate_images(
    prompt="Documentary-style photograph of diverse warehouse workers organizing union meeting",
    number_of_images=1,
    aspect_ratio="16:9",
    safety_settings={
        "block_none": False,
        "block_low": False,
        "block_medium": True,
        "block_high": True
    }
)

# Access generated image
image = response.images[0]
image_bytes = image._pil_image.tobytes()  # Get raw bytes
image_pil = image._pil_image  # Get PIL Image object
```

### Complete Request Parameters

```python
response = model.generate_images(
    prompt: str,                    # REQUIRED: Text description (max 2000 chars)
    number_of_images: int = 1,      # Number of images to generate (1-4)
    aspect_ratio: str = "16:9",     # Options: "1:1", "16:9", "9:16", "4:3", "3:4"
    negative_prompt: str = None,    # What to avoid (e.g., "blurry, distorted")
    safety_settings: dict = None,   # Safety filter configuration
    guidance_scale: float = 7.0,    # Prompt adherence (1.0-20.0, higher = stricter)
    seed: int = None                # Reproducibility seed (optional)
)
```

### Parameter Details

**prompt** (string, required)
- Maximum length: 2000 characters
- Best results: 50-500 characters
- Include: subject, style, mood, technical requirements
- Example: "Photojournalistic image of striking auto workers holding union signs, documentary style, diverse group, dignified and empowering, horizontal 16:9 format"

**number_of_images** (integer, 1-4)
- Default: 1
- MVP recommendation: 1 (cost optimization)
- Use case for >1: Generate multiple options for editor selection

**aspect_ratio** (string)
- Options: `"1:1"`, `"16:9"`, `"9:16"`, `"4:3"`, `"3:4"`
- Recommendation: `"16:9"` (standard news article format)
- Note: Actual pixel dimensions determined by model (typically 1024-2048px wide)

**negative_prompt** (string, optional)
- What to exclude from generation
- Examples: "low quality, blurry, distorted, text, watermark, signature, cartoon, anime"
- Recommendation: Always include basic quality filters

**safety_settings** (dict, optional)
- Control content safety filtering
- Categories: `harassment`, `hate_speech`, `sexually_explicit`, `dangerous_content`
- Levels: `block_none`, `block_low`, `block_medium`, `block_high`
- Default: `block_medium` for all categories

**guidance_scale** (float, 1.0-20.0)
- Controls how strictly the model follows the prompt
- Lower (1-5): More creative, less literal
- Medium (6-10): Balanced (recommended)
- Higher (11-20): Very literal, less creative
- Default: 7.0

**seed** (integer, optional)
- For reproducible generations
- Same prompt + same seed = same image
- Use case: Debugging, A/B testing

---

## Response Format

### Success Response Structure

```python
# Response object
response = ImageGenerationResponse(
    images=[
        GeneratedImage(
            _pil_image=PIL.Image,          # PIL Image object
            _mime_type="image/png",        # Always PNG
            generation_config={...},       # Configuration used
            safety_ratings=[...]           # Safety filter results
        )
    ],
    prompt_feedback=PromptFeedback(
        block_reason=None,                 # None if not blocked
        safety_ratings=[...]               # Safety ratings for prompt
    )
)

# Access image data
image = response.images[0]

# Method 1: Get PIL Image (recommended)
pil_image = image._pil_image
pil_image.save("output.png")

# Method 2: Get bytes directly
from io import BytesIO
buffer = BytesIO()
image._pil_image.save(buffer, format="PNG")
image_bytes = buffer.getvalue()

# Method 3: Get base64 encoded
import base64
buffer = BytesIO()
image._pil_image.save(buffer, format="PNG")
image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
```

### Safety Ratings Structure

```python
safety_ratings = [
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "probability": "NEGLIGIBLE"  # Options: NEGLIGIBLE, LOW, MEDIUM, HIGH
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "probability": "NEGLIGIBLE"
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "probability": "NEGLIGIBLE"
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "probability": "NEGLIGIBLE"
    }
]
```

---

## Error Handling

### Common Errors

**1. Authentication Error**
```python
# Error: google.api_core.exceptions.Unauthenticated
# Cause: Invalid or missing API key
# Solution: Verify GEMINI_API_KEY is set correctly

try:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-2.5-flash-image')
except Exception as e:
    logger.error(f"Authentication failed: {e}")
    # Fallback to stock photos
```

**2. Safety Filter Blocked**
```python
# Error: response.prompt_feedback.block_reason is not None
# Cause: Prompt triggered safety filters
# Solution: Revise prompt or adjust safety settings

if response.prompt_feedback.block_reason:
    logger.warning(f"Image generation blocked: {response.prompt_feedback.block_reason}")
    # Fallback to alternative prompt or stock photos
```

**3. Rate Limit Exceeded**
```python
# Error: google.api_core.exceptions.ResourceExhausted
# Cause: Exceeded 60 requests/minute or 1500 requests/day
# Solution: Implement exponential backoff and retry

from google.api_core import retry

@retry.Retry(predicate=retry.if_exception_type(
    google.api_core.exceptions.ResourceExhausted
))
def generate_with_retry():
    return model.generate_images(prompt=prompt, ...)
```

**4. Invalid Prompt**
```python
# Error: google.api_core.exceptions.InvalidArgument
# Cause: Prompt too long (>2000 chars) or invalid parameters
# Solution: Validate and truncate prompt

if len(prompt) > 2000:
    prompt = prompt[:1997] + "..."
```

### Retry Logic Implementation

```python
import time
from google.api_core import exceptions

def generate_with_gemini(prompt: str, max_retries: int = 3) -> Optional[bytes]:
    """Generate image with exponential backoff retry"""

    for attempt in range(max_retries):
        try:
            response = model.generate_images(
                prompt=prompt,
                number_of_images=1,
                aspect_ratio="16:9"
            )

            # Check for safety blocks
            if response.prompt_feedback.block_reason:
                logger.warning(f"Prompt blocked: {response.prompt_feedback.block_reason}")
                return None

            # Extract image bytes
            buffer = BytesIO()
            response.images[0]._pil_image.save(buffer, format="PNG")
            return buffer.getvalue()

        except exceptions.ResourceExhausted:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s
                logger.info(f"Rate limit hit, retrying in {wait_time}s...")
                time.sleep(wait_time)
            else:
                logger.error("Rate limit exceeded after max retries")
                return None

        except exceptions.InvalidArgument as e:
            logger.error(f"Invalid request parameters: {e}")
            return None

        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
            else:
                return None

    return None
```

---

## Performance Characteristics

### Latency

| Aspect | Measurement |
|--------|-------------|
| Average generation time | 10-15 seconds |
| P95 generation time | 20 seconds |
| P99 generation time | 30 seconds |
| Network overhead | 1-2 seconds |
| **Total end-to-end** | **12-17 seconds typical** |

### Throughput

- **Rate limits:** 60 requests/minute, 1500 requests/day (free tier)
- **Recommended rate:** 30-40 requests/minute (buffer for safety)
- **Daily capacity:** 1500 images/day (sufficient for 3-10 articles/day MVP)

### Cost Analysis

| Tier | Cost per Image | Daily Budget ($0.50) | Monthly Budget ($15) |
|------|----------------|---------------------|---------------------|
| Free tier | $0 | Unlimited (1500/day limit) | Unlimited |
| Paid (Flash) | $0.02-0.04 | 12-25 images | 375-750 images |
| Paid (Pro) | $0.10-0.15 | 3-5 images | 100-150 images |

**MVP Recommendation:** Use free tier (1500/day = 150-500 articles/day capacity)

---

## Image Quality Specifications

### Output Characteristics

- **Format:** PNG (lossless)
- **Color depth:** 24-bit RGB
- **Typical dimensions:** 1024x576 (16:9 at ~1K), 1536x864 (16:9 at ~1.5K)
- **File size:** 500KB - 2MB (PNG), 100-400KB (after JPEG conversion)
- **Quality:** High-fidelity, photorealistic or stylized based on prompt

### Post-Processing Pipeline

```python
from PIL import Image
from io import BytesIO

def optimize_generated_image(image_bytes: bytes) -> bytes:
    """Optimize Gemini-generated image for web"""

    # Load PNG from Gemini
    img = Image.open(BytesIO(image_bytes))

    # Resize if too large (max 1200px width for web)
    if img.width > 1200:
        ratio = 1200 / img.width
        new_height = int(img.height * ratio)
        img = img.resize((1200, new_height), Image.Resampling.LANCZOS)

    # Convert to JPEG for smaller file size
    output = BytesIO()
    img.convert('RGB').save(output, format='JPEG', quality=85, optimize=True)

    return output.getvalue()
```

---

## Security & Safety

### Content Safety

Gemini 2.5 Flash Image includes built-in safety filters:

1. **Harassment:** Blocks abusive, threatening, or derogatory content
2. **Hate Speech:** Blocks content promoting hatred based on protected attributes
3. **Sexually Explicit:** Blocks adult or suggestive content
4. **Dangerous Content:** Blocks content promoting violence, self-harm, or illegal activity

### Safety Filter Configuration

**For news journalism (recommended):**
```python
safety_settings = {
    "harassment": "block_medium",          # Allow critical journalism
    "hate_speech": "block_high",           # Strictly block hate content
    "sexually_explicit": "block_high",     # Block explicit content
    "dangerous_content": "block_medium"    # Allow reporting on violence/danger
}
```

### API Key Security

**Best Practices:**
1. Store in environment variables (never commit to git)
2. Use Secret Manager in production (GCP Secret Manager)
3. Rotate keys every 90 days
4. Monitor usage for anomalies
5. Restrict API key to specific services (API key scoping)

---

## Migration from Vertex AI Imagen

### Key Differences

| Aspect | Vertex AI Imagen | Gemini 2.5 Flash Image |
|--------|------------------|------------------------|
| SDK | `google-cloud-aiplatform` | `google-genai` |
| Auth | Service account JSON | API key (simpler) |
| Endpoint | REST API with project ID | SDK method call |
| Response format | Base64 in JSON | PIL Image object |
| Setup complexity | High (GCP project, IAM) | Low (just API key) |
| Generation time | 20-30s | 10-15s |
| Image quality | Good | Excellent |
| Prompt adherence | Moderate | Strong |

### Code Migration

**Old (Vertex AI Imagen):**
```python
from google.cloud import aiplatform

endpoint = f"https://us-central1-aiplatform.googleapis.com/v1/projects/{project}/locations/us-central1/publishers/google/models/imagegeneration:predict"

response = requests.post(
    endpoint,
    json={"instances": [{"prompt": prompt}], "parameters": {...}},
    headers={"Authorization": f"Bearer {token}"}
)

image_base64 = response.json()['predictions'][0]['bytesBase64Encoded']
image_bytes = base64.b64decode(image_base64)
```

**New (Gemini 2.5 Flash Image):**
```python
import google.generativeai as genai

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.5-flash-image')

response = model.generate_images(prompt=prompt, aspect_ratio="16:9")

buffer = BytesIO()
response.images[0]._pil_image.save(buffer, format="PNG")
image_bytes = buffer.getvalue()
```

**Lines of code:** 15 → 6 (60% reduction)

---

## Testing & Validation

### Unit Test Example

```python
import unittest
from backend.services.image_generation import GeminiImageGenerator

class TestGeminiImageGeneration(unittest.TestCase):

    def setUp(self):
        self.generator = GeminiImageGenerator()

    def test_generate_simple_prompt(self):
        """Test basic image generation"""
        prompt = "Photographic image of workers in professional setting"
        result = self.generator.generate(prompt)

        self.assertIsNotNone(result)
        self.assertIn('image_data', result)
        self.assertGreater(len(result['image_data']), 1000)  # Non-empty

    def test_prompt_length_limit(self):
        """Test prompt truncation for >2000 chars"""
        long_prompt = "A" * 2500
        result = self.generator.generate(long_prompt)

        # Should truncate, not error
        self.assertIsNotNone(result)

    def test_safety_filter_handling(self):
        """Test handling of blocked prompts"""
        blocked_prompt = "violent graphic imagery"
        result = self.generator.generate(blocked_prompt)

        # Should return None or fallback, not crash
        self.assertTrue(result is None or result.get('source_type') == 'fallback')

    def test_retry_on_rate_limit(self):
        """Test exponential backoff on rate limit"""
        # Mock rate limit error
        with patch('google.generativeai.GenerativeModel.generate_images') as mock:
            mock.side_effect = [
                exceptions.ResourceExhausted("Rate limit"),
                self._mock_success_response()
            ]

            result = self.generator.generate_with_retry("test prompt")

            # Should retry and succeed
            self.assertIsNotNone(result)
            self.assertEqual(mock.call_count, 2)
```

### Integration Test Checklist

- [ ] API key authentication works
- [ ] Image generation succeeds with valid prompt
- [ ] Safety filters block inappropriate prompts
- [ ] Rate limiting handled gracefully
- [ ] Retry logic works with exponential backoff
- [ ] Image optimization pipeline functions
- [ ] File storage and database recording works
- [ ] Fallback to stock photos on failure
- [ ] Cost tracking accurate
- [ ] Generated images meet quality standards

---

## References

- **Official Documentation:** https://ai.google.dev/gemini-api/docs/imagen
- **SDK Reference:** https://pypi.org/project/google-genai/
- **API Key Console:** https://aistudio.google.com/apikey
- **Rate Limits:** https://ai.google.dev/gemini-api/docs/quota
- **Safety Filters:** https://ai.google.dev/gemini-api/docs/safety-settings

---

**Document Status:** Complete
**Next Steps:** See `CLAUDE_PROMPT_ENHANCEMENT_WORKFLOW.md` for Claude integration design
