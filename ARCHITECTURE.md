# System Architecture

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLIENT LAYER                             │
├─────────────────────────────────────────────────────────────────┤
│  Web Browser          Mobile App         Desktop App             │
│  (demo.html)          (React/Vue)        (Electron)              │
└────────────┬────────────────────┬────────────────┬──────────────┘
             │                    │                │
             └────────────────────┼────────────────┘
                                  │
                         HTTP POST /chat
                    (multipart: image + query)
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                      FASTAPI SERVER                              │
│                         (main.py)                                │
├─────────────────────────────────────────────────────────────────┤
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  API Endpoints:                                           │  │
│  │  • POST /chat    - Image + Query → AI Response          │  │
│  │  • GET  /stats   - Usage Statistics                     │  │
│  │  • GET  /health  - Health Check                         │  │
│  │  • GET  /info    - API Information                      │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                  │                               │
│  ┌───────────────────────────────▼──────────────────────────┐   │
│  │  Request Processing Pipeline:                           │   │
│  │  1. Validate image (JPEG/PNG, max 10MB)                │   │
│  │  2. Read image file                                     │   │
│  │  3. Convert to PIL Image                                │   │
│  │  4. Call Model Layer                                    │   │
│  │  5. Return JSON response                                │   │
│  └─────────────────────────────────────────────────────────┘   │
└────────────┬────────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────────┐
│                       MODEL LAYER                                │
│                       (model.py)                                 │
├─────────────────────────────────────────────────────────────────┤
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  GeminiVisionModel Class:                                │  │
│  │  • Singleton pattern                                     │  │
│  │  • Manages API client                                    │  │
│  │  • Handles preprocessing                                 │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                  │                               │
│  ┌───────────────────────────────▼──────────────────────────┐   │
│  │  Processing Steps:                                       │   │
│  │  1. Preprocess Image (GPU/CPU)                          │   │
│  │  │   └─> Resize to 1024x1024                           │   │
│  │  │   └─> Convert to RGB                                │   │
│  │  │   └─> Apply transforms (PyTorch)                    │   │
│  │  2. Create Prompt                                       │   │
│  │  │   └─> Add context and instructions                  │   │
│  │  3. Call Gemini API                                     │   │
│  │  4. Parse Response                                      │   │
│  │  5. Return text                                         │   │
│  └─────────────────────────────────────────────────────────┘   │
└────────────┬────────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────────┐
│                   IMAGE PREPROCESSING                            │
│                   (PyTorch + GPU)                                │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────┐         ┌──────────────────────────┐   │
│  │   GPU Available?    │   YES   │   GPU Processing Path    │   │
│  │   (CUDA Detected)   ├────────>│   • Load to CUDA         │   │
│  │                     │         │   • GPU transforms       │   │
│  │                     │         │   • Move back to CPU     │   │
│  └──────────┬──────────┘         └──────────────────────────┘   │
│             │ NO                                                 │
│             ▼                                                    │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │   CPU Processing Path                                    │   │
│  │   • PIL resize                                           │   │
│  │   • Basic transforms                                     │   │
│  └──────────────────────────────────────────────────────────┘   │
└────────────┬────────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    GOOGLE GEMINI API                             │
│                  (External Service)                              │
├─────────────────────────────────────────────────────────────────┤
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  Gemini-1.5-Flash / Gemini-1.5-Pro                      │  │
│  │  • Vision-Language Model                                │  │
│  │  • Multimodal Input (text + image)                      │  │
│  │  • Food product analysis                                │  │
│  │  • Structured responses                                 │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                  │                               │
│  ┌───────────────────────────────▼──────────────────────────┐   │
│  │  Analysis Capabilities:                                  │   │
│  │  ✓ Product identification                               │   │
│  │  ✓ Ingredient extraction                                │   │
│  │  ✓ Nutrition information                                │   │
│  │  ✓ Allergen detection                                   │   │
│  │  ✓ Dietary classification                               │   │
│  │  ✓ Health recommendations                               │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘


## Data Flow Diagram

┌─────────┐
│  User   │
│ Uploads │
│  Image  │
└────┬────┘
     │
     ▼
┌─────────────────┐
│  Image File     │
│  + Text Query   │
└────┬────────────┘
     │
     ▼
┌─────────────────────────────┐
│  FastAPI                    │
│  • Validate format          │
│  • Check size               │
│  • Parse multipart          │
└────┬────────────────────────┘
     │
     ▼
┌─────────────────────────────┐
│  Image Preprocessing        │
│  GPU Path:                  │
│  • PIL → Tensor → CUDA      │
│  • Transform on GPU         │
│  • Tensor → PIL             │
│                             │
│  CPU Path:                  │
│  • PIL resize               │
│  • Format conversion        │
└────┬────────────────────────┘
     │
     ▼
┌─────────────────────────────┐
│  Prompt Engineering         │
│  • Create context           │
│  • Add user query           │
│  • Structure instructions   │
└────┬────────────────────────┘
     │
     ▼
┌─────────────────────────────┐
│  Gemini API Call            │
│  • Send image + prompt      │
│  • Wait for response        │
│  • Handle rate limits       │
└────┬────────────────────────┘
     │
     ▼
┌─────────────────────────────┐
│  Response Processing        │
│  • Extract text             │
│  • Format output            │
│  • Add metadata             │
└────┬────────────────────────┘
     │
     ▼
┌─────────────────────────────┐
│  JSON Response              │
│  {                          │
│    "response": "...",       │
│    "timestamp": "...",      │
│    "processing_time": 1.23  │
│  }                          │
└────┬────────────────────────┘
     │
     ▼
┌─────────┐
│  User   │
│ Receives│
│ Answer  │
└─────────┘


## Component Interactions

┌──────────────────────────────────────────────────────────────┐
│                        main.py                                │
│  ┌────────────┐  ┌────────────┐  ┌──────────────┐           │
│  │  Endpoint  │  │  Request   │  │   Response   │           │
│  │  Handlers  │──│ Validation │──│  Formatting  │           │
│  └──────┬─────┘  └────────────┘  └──────────────┘           │
│         │                                                     │
│         │ calls                                               │
│         ▼                                                     │
└─────────┼─────────────────────────────────────────────────────┘
          │
          │
┌─────────▼─────────────────────────────────────────────────────┐
│                        model.py                                │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │          GeminiVisionModel (Singleton)                   │ │
│  │  ┌──────────┐  ┌───────────┐  ┌─────────────┐          │ │
│  │  │   API    │  │   Image   │  │   Prompt    │          │ │
│  │  │  Client  │  │Preprocess │  │ Engineering │          │ │
│  │  └──────────┘  └───────────┘  └─────────────┘          │ │
│  └──────────────────────────────────────────────────────────┘ │
│         │                  │                                   │
│         │                  │ uses                              │
│         │                  ▼                                   │
│         │        ┌─────────────────┐                          │
│         │        │    PyTorch      │                          │
│         │        │    + CUDA       │                          │
│         │        └─────────────────┘                          │
│         │                                                      │
└─────────┼──────────────────────────────────────────────────────┘
          │
          │ calls
          ▼
┌──────────────────────────────────────────────────────────────┐
│              Google Gemini API (External)                     │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │  google.generativeai library                            │ │
│  │  • genai.configure(api_key)                             │ │
│  │  • GenerativeModel(model_name)                          │ │
│  │  • generate_content([prompt, image])                    │ │
│  └─────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────┘


## Technology Stack Layers

┌─────────────────────────────────────────────────────────────┐
│  Frontend Layer (Optional)                                   │
│  • HTML/CSS/JavaScript (demo.html)                          │
│  • React/Vue/Angular (future frontend)                      │
└─────────────────────────────────────────────────────────────┘
                           │
                           │ HTTP/REST
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  Web Framework                                               │
│  • FastAPI 0.104.1                                          │
│  • Uvicorn (ASGI server)                                    │
│  • CORS middleware                                          │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  Application Logic                                           │
│  • Request validation (Pydantic)                            │
│  • File handling (multipart)                                │
│  • Statistics tracking                                       │
│  • Error handling                                           │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  Image Processing                                            │
│  • Pillow (PIL) - Image manipulation                        │
│  • PyTorch - Tensor operations                              │
│  • torchvision - Transforms                                 │
│  • CUDA - GPU acceleration                                  │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  AI Integration                                              │
│  • google-generativeai library                              │
│  • API key authentication                                   │
│  • Request/response handling                                │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  External AI Service                                         │
│  • Google Gemini API                                        │
│  • Vision-Language Models                                   │
│  • Cloud-based processing                                   │
└─────────────────────────────────────────────────────────────┘
