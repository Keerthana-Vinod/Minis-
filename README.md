# 🍕 Food Product Assistant

A comprehensive AI-powered food analysis system that combines computer vision, natural language processing, and nutritional science to provide detailed insights about food products from images.

## 🌟 Overview

The Food Product Assistant is a full-stack web application that uses Google's Gemini AI to analyze food product images and provide:

- **Exact Brand Identification** (Coca-Cola, Pepsi, Fanta, etc.)
- **Complete Nutritional Analysis** (calories, macros, vitamins)
- **Ingredient Breakdown** with detailed composition
- **Health-Oriented Recommendations** based on dietary guidelines
- **Allergen Detection** and safety warnings
- **Visual Product Recognition** using hybrid AI models

## 🏗️ Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (Web App)                       │
│  ┌─────────────────┬─────────────────┬─────────────────┐   │
│  │  index_new.html │   detail.html   │     app.js       │   │
│  │                 │                 │                 │   │
│  │ • Image Upload  │ • Results Display│ • API Client    │   │
│  │ • Drag & Drop   │ • Data Viz       │ • State Mgmt    │   │
│  │ • Real-time UI  │ • Health Ratings │ • Error Handling│   │
│  └─────────────────┴─────────────────┴─────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                                 │
                    ┌────────────────────┐
                    │   FastAPI Backend  │
                    │  ┌─────────────┐   │
                    │  │   /analyze  │   │
                    │  │   /chat     │   │
                    │  │   /health   │   │
                    │  └─────────────┘   │
                    └────────────────────┘
                                 │
                    ┌────────────────────┐
                    │   AI Model Layer   │
                    │  ┌─────────────┐   │
                    │  │   Gemini    │   │
                    │  │   API       │   │
                    │  │  (Primary)  │   │
                    │  └─────────────┘   │
                    │  ┌─────────────┐   │
                    │  │   Gemma     │   │
                    │  │   (Fallback)│   │
                    │  └─────────────┘   │
                    │  ┌─────────────┐   │
                    │  │  ResNet50   │   │
                    │  │  (Local Vision)│   │
                    │  └─────────────┘   │
                    └────────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- **Python 3.8+**
- **Google Gemini API Key** ([Get one here](https://makersuite.google.com/app/apikey))
- **Modern Web Browser** (Chrome 70+, Firefox 65+, Safari 12+)
- **Optional**: NVIDIA GPU for accelerated processing

### Installation

1. **Clone/Download the project**
```bash
cd /home/gokul-p/Project/Minis_Backend
```

2. **Install Python dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure API Key**
```bash
# Edit .env file
GEMINI_API_KEY="your_actual_api_key_here"
```

4. **Start the server**
```bash
# Linux/Mac
./start.sh

# Windows
start.bat

# Or manually
python main.py
```

5. **Open your browser**
```
http://localhost:8000
```

## 📱 User Guide

### Basic Usage

1. **Upload Image**: Click "Analyze Food" or drag & drop an image
2. **Wait for Analysis**: AI processes the image (2-4 seconds)
3. **View Results**: Detailed nutritional breakdown and health recommendations

### Supported Products

- **Sodas**: Coca-Cola, Pepsi, Sprite, Fanta, Dr Pepper
- **Snacks**: Chips, cookies, granola bars
- **Dairy**: Milk, yogurt, cheese
- **Packaged Foods**: Canned goods, frozen meals
- **Fresh Produce**: Fruits, vegetables (limited analysis)

### Example Analysis Output

```
🍎 Product: Coca-Cola Classic
📏 Serving Size: 355ml (12 fl oz)
🔥 Calories: 140 kcal
🥔 Carbohydrates: 39g
💪 Protein: 0g
🧈 Fats: 0g
🍬 Sugar: 39g

Key Ingredients:
• Carbonated water
• High fructose corn syrup
• Caramel color
• Phosphoric acid
• Natural flavors
• Caffeine

Health Rating: 🍊 Occasional
Recommendation: Enjoy occasionally as part of a balanced diet. High sugar content.
```

## 🔧 Technical Details

### Backend API

#### Core Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `GET /` | GET | Main web interface |
| `POST /analyze` | POST | Image analysis (structured JSON) |
| `POST /chat` | POST | Interactive Q&A about products |
| `GET /health` | GET | System health check |
| `GET /stats` | GET | Usage statistics |

#### API Response Format

```json
{
  "success": true,
  "data": {
    "name": "Coca-Cola Classic",
    "description": "This is Coca-Cola Classic. Each 355ml contains 140 calories...",
    "weight": "355ml",
    "nutrition": {
      "calories": 140,
      "carbs": 39,
      "protein": 0,
      "fats": 0,
      "sugar": 39
    },
    "ingredients": ["carbonated water", "high fructose corn syrup"],
    "healthRating": "occasional",
    "recommendation": "Enjoy occasionally as part of a balanced diet"
  },
  "processing_time": 2.34
}
```

### AI Model Pipeline

#### 1. Image Preprocessing
- **Format**: Convert to RGB, resize to 1024x1024
- **GPU Acceleration**: Automatic CUDA detection
- **Optimization**: Lanczos resampling for quality

#### 2. Hybrid Analysis System

**Primary Path (Gemini API):**
```
Image → Gemini 1.5 Flash/Pro → Structured JSON → Frontend Display
```

**Fallback Path (Quota/Errors):**
```
Image → Local ResNet50 → Basic Object Detection → Gemma Text → JSON → Display
```

**Demo Mode (No API):**
```
Image → Mock Analysis → Sample Data → Educational Content
```

#### 3. Prompt Engineering

**Brand Identification Prompt:**
```
Identify the SPECIFIC food product... Look for BRAND NAME: Coca-Cola, Pepsi-Cola...
OUTPUT ONLY JSON with exact brand and model...
```

**Nutritional Analysis Prompt:**
```
Analyze this food product... Provide EXACT format:
Product Name: [name]
Description: [description]
Weight/Serving Size: [weight]
Nutritional Information (per 100g): [nutrition]
Health Rating: [Safe/Occasional/High Risk]
```

### Frontend Architecture

#### Progressive Enhancement

```html
<!-- Basic HTML (works everywhere) -->
<form action="/analyze" method="post" enctype="multipart/form-data">
    <input type="file" name="image" accept="image/*">
    <button type="submit">Analyze</button>
</form>

<!-- Enhanced JavaScript (modern browsers) -->
<script>
    // Async upload, real-time preview, progress indicators
    initializeModernFeatures();
</script>
```

#### State Management

```javascript
const AppState = {
    currentFood: null,           // Current analysis result
    uploadedImage: null,         // Base64 image data
    analysisHistory: [],         // Last 10 analyses
    
    // Automatic localStorage persistence
    setCurrentFood(food) {
        this.currentFood = food;
        localStorage.setItem('currentFood', JSON.stringify(food));
    }
};
```

#### JSON Parsing Resilience

The frontend implements sophisticated JSON extraction to handle various AI response formats:

```javascript
function parseRawFoodAnalysis(rawText) {
    // 1. Try markdown code blocks: ```json{...}```
    // 2. Fallback: Manual brace counting for JSON extraction
    // 3. Parse and validate JSON structure
    // 4. Map to frontend data format
    // 5. Generate health-oriented descriptions
}
```

## 🎨 User Interface

### Design Philosophy

- **Health-Focused**: Green color palette, clean typography
- **Mobile-First**: Responsive design for all devices
- **Accessible**: WCAG 2.1 AA compliance, keyboard navigation
- **Progressive**: Works without JavaScript, enhanced with it

### Key Features

#### Upload Interface
- **Drag & Drop**: Modern file upload experience
- **Image Preview**: Real-time thumbnail generation
- **Format Validation**: JPEG/PNG only, 10MB limit
- **Progress Indicators**: Visual feedback during analysis

#### Results Display
- **Nutritional Table**: Comprehensive macro breakdown
- **Health Ratings**: Color-coded safety indicators
- **Ingredient List**: Interactive ingredient details
- **Visual Charts**: Pie charts for nutritional composition

#### Responsive Design

```css
/* Mobile First */
@media (max-width: 768px) {
    .main-grid { grid-template-columns: 1fr; }
    .nutrition-summary { grid-template-columns: repeat(2, 1fr); }
}

/* Desktop Enhancement */
@media (min-width: 1025px) {
    .nutrition-summary { grid-template-columns: repeat(6, 1fr); }
    .container { max-width: 1400px; }
}
```

## 🔒 Security & Privacy

### Data Protection

- **No Image Storage**: Images processed in-memory only
- **No User Data**: Anonymous analysis, no personal information
- **Secure Transmission**: HTTPS recommended for production
- **API Key Protection**: Server-side only, never exposed to frontend

### Input Validation

```python
# Backend validation
def validate_image(file):
    if file.content_type not in ["image/jpeg", "image/png"]:
        raise HTTPException(400, "Invalid file type")
    if file.size > 10 * 1024 * 1024:  # 10MB
        raise HTTPException(400, "File too large")
```

### Rate Limiting

```python
# Recommended nginx configuration
limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
limit_req zone=api burst=20 nodelay;
```

## 📊 Performance

### Benchmarks

| Operation | Time | Notes |
|-----------|------|-------|
| Image Upload | 0.1-0.5s | Network dependent |
| Local Vision | 0.2-0.8s | GPU: 0.2s, CPU: 0.8s |
| Gemini API | 1.0-3.0s | Model dependent |
| JSON Parsing | 0.05-0.2s | Frontend processing |
| **Total** | **2-4s** | End-to-end analysis |

### Optimization Features

#### GPU Acceleration
- **Automatic Detection**: CUDA availability check
- **Fallback Handling**: Graceful CPU fallback
- **Memory Management**: Efficient tensor operations

#### Caching Strategy
- **Model Singleton**: Single model instance across requests
- **Connection Reuse**: Persistent HTTP connections
- **Response Caching**: Optional Redis integration

#### Frontend Performance
- **Lazy Loading**: Images loaded on demand
- **Code Splitting**: Modular JavaScript loading
- **Memory Cleanup**: Automatic resource management

## 🧪 Testing

### API Testing

```bash
# Test with curl
curl -X POST http://localhost:8000/analyze \
  -F "image=@coca_cola.jpg"

# Test with Python
python test_api.py
```

### Frontend Testing

```javascript
// Manual testing checklist
✅ File upload (click, drag, paste)
✅ Image validation (format, size)
✅ Loading states (progress, feedback)
✅ Error handling (network, invalid file)
✅ Results display (nutrition, ingredients)
✅ Responsive design (mobile, tablet, desktop)
✅ Accessibility (keyboard, screen readers)
```

### Automated Testing

```bash
# Run backend tests
pytest

# Frontend unit tests (if implemented)
npm test

# Integration tests
python test_integration.py
```

## 🚀 Deployment

### Development

```bash
# Local development
python main.py

# With auto-reload
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Production

#### Docker Deployment

```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

#### Nginx + Gunicorn

```nginx
upstream food_api {
    server 127.0.0.1:8000;
    server 127.0.0.1:8001;
    server 127.0.0.1:8002;
    server 127.0.0.1:8003;
}

server {
    listen 80;
    server_name yourdomain.com;
    
    location / {
        proxy_pass http://food_api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Environment Configuration

```env
# Production Settings
DEBUG=false
PORT=8000
HOST=0.0.0.0

# Security
ALLOWED_ORIGINS=https://yourdomain.com

# Performance
WORKERS=4
MAX_REQUESTS_PER_WORKER=1000

# Monitoring
LOG_LEVEL=INFO
```

## 🔧 Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `GEMINI_API_KEY` | - | **Required**: Google Gemini API key |
| `MODEL_NAME` | `gemini-1.5-flash` | AI model to use |
| `USE_GPU` | `true` | Enable GPU acceleration |
| `PORT` | `8000` | Server port |
| `DEBUG` | `true` | Enable debug mode |
| `MAX_TOKENS` | `2048` | Maximum response length |

### Model Configuration

```env
# Fast and cost-effective (recommended)
MODEL_NAME=gemini-1.5-flash

# Higher quality but slower/more expensive
MODEL_NAME=gemini-1.5-pro

# Enable hybrid mode for quota management
USE_HYBRID_MODE=true
```

## 🐛 Troubleshooting

### Common Issues

#### "Model not loaded" Error
```
Cause: Missing or invalid Gemini API key
Solution: Check GEMINI_API_KEY in .env file
```

#### "CUDA out of memory" Error
```
Cause: GPU memory insufficient
Solution: Set USE_GPU=false or reduce batch size
```

#### "JSON parsing failed" Error
```
Cause: AI returned malformed response
Solution: Check raw response in logs, update prompts
```

#### Slow Performance
```
Cause: Network latency or large images
Solution: Optimize image size, use faster model
```

### Debug Mode

Enable detailed logging:
```env
DEBUG=true
LOG_LEVEL=DEBUG
```

### Health Checks

```bash
# API health
curl http://localhost:8000/health

# Statistics
curl http://localhost:8000/stats
```

## 📈 Monitoring

### Built-in Metrics

- **Request Count**: Total, successful, failed requests
- **Processing Time**: Average analysis time
- **Error Rate**: API and processing errors
- **Model Status**: API availability, fallback usage

### External Monitoring

```python
# Prometheus metrics (example)
from prometheus_client import Counter, Histogram

REQUEST_COUNT = Counter('food_api_requests_total', 'Total requests')
PROCESSING_TIME = Histogram('food_api_processing_seconds', 'Processing time')
```

## 🤝 API Integration

### JavaScript Client

```javascript
async function analyzeFood(imageFile) {
    const formData = new FormData();
    formData.append('image', imageFile);
    
    const response = await fetch('/analyze', {
        method: 'POST',
        body: formData
    });
    
    const result = await response.json();
    return result.data;
}
```

### Python Client

```python
import requests

def analyze_product(image_path):
    with open(image_path, 'rb') as f:
        files = {'image': f}
        response = requests.post('http://localhost:8000/analyze', files=files)
        return response.json()
```

### Mobile App Integration

```swift
// iOS example
func uploadImage(_ image: UIImage) async throws -> FoodAnalysis {
    let imageData = image.jpegData(compressionQuality: 0.8)!
    
    let url = URL(string: "http://your-api.com/analyze")!
    var request = URLRequest(url: url)
    request.httpMethod = "POST"
    
    let boundary = UUID().uuidString
    request.setValue("multipart/form-data; boundary=\(boundary)", forHTTPHeaderField: "Content-Type")
    
    // Create multipart body...
    let (data, _) = try await URLSession.shared.data(for: request)
    return try JSONDecoder().decode(FoodAnalysis.self, from: data)
}
```

## 🔄 Updates & Maintenance

### Version History

#### v1.0.0 (Current)
- ✅ Gemini API integration
- ✅ Hybrid local vision fallback
- ✅ Health-oriented descriptions
- ✅ Responsive web interface
- ✅ GPU acceleration support

#### Planned v1.1.0
- 🔄 Batch processing (multiple images)
- 🔄 Recipe generation
- 🔄 Barcode scanning
- 🔄 Offline PWA mode

### Updating Dependencies

```bash
# Update Python packages
pip install --upgrade -r requirements.txt

# Update specific package
pip install google-generativeai==0.3.2

# Check for security updates
pip audit
```

## 📚 Documentation

### Detailed Documentation

- **[Backend Documentation](BACKEND_DOCUMENTATION.md)**: Complete API reference, architecture details
- **[Frontend Documentation](FRONTEND_DOCUMENTATION.md)**: UI/UX design, JavaScript implementation
- **[Setup Guide](SETUP.md)**: Step-by-step installation instructions
- **[API Reference](api.md)**: Interactive API documentation

### API Documentation

Once running, visit:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## 🤝 Contributing

### Development Setup

1. **Fork the repository**
2. **Create feature branch**: `git checkout -b feature/new-feature`
3. **Install dependencies**: `pip install -r requirements.txt`
4. **Run tests**: `pytest`
5. **Submit pull request**

### Code Standards

- **Python**: PEP 8, type hints, docstrings
- **JavaScript**: ESLint, modern ES6+ features
- **HTML/CSS**: Semantic markup, BEM methodology
- **Testing**: 80%+ code coverage required

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Support

### Getting Help

1. **Check the documentation**: [Backend Docs](BACKEND_DOCUMENTATION.md), [Frontend Docs](FRONTEND_DOCUMENTATION.md)
2. **Review troubleshooting**: Common issues and solutions above
3. **Check logs**: Enable DEBUG mode for detailed logging
4. **Community**: Open GitHub issue for bugs/features

### Professional Support

For enterprise deployment, custom integrations, or priority support:
- Contact: [your-email@example.com]
- Enterprise licensing available

---

## 🎯 Use Cases

### For Consumers
- **Diet Planning**: Track nutritional intake
- **Allergen Awareness**: Identify hidden allergens
- **Health Monitoring**: Make informed food choices
- **Educational**: Learn about food composition

### For Developers
- **AI Integration**: Food analysis API for apps
- **Research**: Nutritional data collection
- **Education**: Interactive food science tool
- **Health Tech**: Integration with fitness apps

### For Businesses
- **Product Analysis**: Competitor product intelligence
- **Quality Control**: Automated product verification
- **Nutrition Labeling**: Automated nutritional facts
- **Food Safety**: Allergen and contamination detection

---

**Built with ❤️ using FastAPI, Google's Gemini AI, and modern web technologies.**

*Last updated: January 4, 2026*
  "uptime_seconds": 3600.5,
  "start_time": "2025-12-30T09:00:00"
}
```

#### `GET /health`
Health check endpoint.

#### `GET /info`
Detailed API information and features.

## � API Endpoints

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- (Optional) CUDA-capable GPU for faster inference

### Installation

1. **Clone or navigate to the project directory:**
```bash
cd /home/gokul-p/Project/Minis_Backend
```

2. **Create a virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Linux/Mac
# or
venv\Scripts\activate  # On Windows
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables:**
```bash
cp .env.example .env
# Edit .env with your configuration
```

Key environment variables:
- `MODEL_NAME`: Gemma model to use (default: "google/gemma-2b-it")
- `MODEL_DEVICE`: "cuda" for GPU or "cpu" for CPU
- `PORT`: Server port (default: 8000)
- `MAX_NEW_TOKENS`: Maximum response length (default: 512)

### Running the Server

#### Development Mode (with auto-reload):
```bash
python main.py
```

#### Production Mode:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

The server will start at: `http://localhost:8000`

## 📚 API Documentation

Once the server is running, visit:
- **Interactive API docs (Swagger UI)**: http://localhost:8000/docs
- **Alternative API docs (ReDoc)**: http://localhost:8000/redoc

## 🧪 Testing the API

### Using cURL:

```bash
# Test root endpoint
curl http://localhost:8000/

# Test chat endpoint
curl -X POST http://localhost:8000/chat \
  -F "image=@/path/to/product_image.jpg" \
  -F "query=What are the ingredients in this product?"

# Get statistics
curl http://localhost:8000/stats

# Health check
curl http://localhost:8000/health
```

### Using Python:

```python
import requests

# Upload image and query
url = "http://localhost:8000/chat"
files = {"image": open("product_image.jpg", "rb")}
data = {"query": "Is this product vegetarian?"}

response = requests.post(url, files=files, data=data)
print(response.json())
```

### Using the Interactive Docs:

1. Navigate to http://localhost:8000/docs
2. Click on the `/chat` endpoint
3. Click "Try it out"
4. Upload an image and enter your query
5. Click "Execute"

## 🏗️ Project Structure

```
Minis_Backend/
├── main.py                 # Main FastAPI application
├── model.py                # Gemma model integration
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables (create from .env.example)
├── .env.example           # Environment variables template
├── README.md              # This file
└── 694e2c4499e34_Encode_PS.pdf  # Project specifications
```


## ⚙️ Configuration

### Environment Variables (`.env`)

Key configuration options:

```env
# Gemini API Configuration
GEMINI_API_KEY="your_api_key_here"          # Required: Get from Google AI Studio
MODEL_NAME="gemini-1.5-flash"                # or "gemini-1.5-pro" for better quality
MAX_TOKENS=2048                              # Maximum response length
TEMPERATURE=0.7                              # Response creativity (0.0-1.0)

# GPU Configuration
USE_GPU=true                                 # Enable/disable GPU acceleration

# Server Configuration
PORT=8000
DEBUG=True
```


### CUDA Installation (for GPU support)

If you have an NVIDIA GPU, install PyTorch with CUDA:

```bash
# For CUDA 11.8
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118

# For CUDA 12.1
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
```

Check GPU availability:
```python
import torch
print(f"GPU Available: {torch.cuda.is_available()}")
print(f"GPU Name: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'N/A'}")
```


### GPU Support

The system automatically detects and uses NVIDIA GPUs for image preprocessing:

- ✅ **GPU Detected**: Automatically enables GPU-accelerated preprocessing
- ❌ **No GPU**: Falls back to CPU preprocessing (still works fine)

To disable GPU even if available:
```env
USE_GPU=false
```

### Model Options

- **gemini-1.5-flash**: Faster, cost-effective (recommended for most cases)
- **gemini-1.5-pro**: Higher quality, more detailed analysis

## 📊 GPU Performance

### Model Configuration

Edit `.env` to customize model settings:

```env
MODEL_NAME="google/gemma-2b-it"  # Change to your preferred Gemma model
MODEL_DEVICE="cuda"              # Use "cpu" if no GPU available
MAX_NEW_TOKENS=512               # Max response length
TEMPERATURE=0.7                  # Response creativity (0.0-1.0)
```

### CORS Configuration

For production, update the `ALLOWED_ORIGINS` in `.env`:

```env
ALLOWED_ORIGINS="https://yourfrontend.com,https://app.yoursite.com"
```

## 🎯 Use Cases

The API can handle queries about:
- **Ingredients**: "What are the ingredients in this product?"
- **Allergens**: "Does this contain nuts or dairy?"
- **Nutrition**: "How many calories per serving?"
- **Dietary Info**: "Is this vegan/vegetarian/gluten-free?"
- **Product Details**: "What brand is this?"


## 🔑 Getting Your Gemini API Key

1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the key and add it to your `.env` file

Note: Gemini API has a free tier with generous limits for development and testing.

- **Shelf Analysis**: "How many products are on this shelf?"

## 🔐 Security Considerations

For production deployment:

1. **Set proper CORS origins** in `.env`
2. **Add authentication** (JWT, API keys)
3. **Implement rate limiting**
4. **Add input validation** for file sizes
5. **Use HTTPS** for encrypted communication
6. **Set file upload limits** (currently 10MB)

## 📊 Performance Tips

- **Use GPU**: Set `MODEL_DEVICE="cuda"` for faster inference
- **Adjust workers**: Use multiple workers in production: `--workers 4`
- **Optimize model**: Use quantized models for faster inference
- **Cache responses**: Implement response caching for common queries
- **Use async operations**: All endpoints are async-capable

## 🐛 Troubleshooting

### Model Loading Issues:
```bash
# If model fails to load, it runs in demo mode
# Check logs for specific errors
# Ensure you have enough RAM/VRAM for the model
```

### Port Already in Use:
```bash
# Change port in .env or use:
uvicorn main:app --port 8001
```

### Image Processing Errors:
- Ensure image is JPEG or PNG format
- Check file size (max 10MB by default)
- Verify image is not corrupted

## 📝 Development

### Adding New Features:

1. **New endpoints**: Add routes in `main.py`
2. **Model improvements**: Modify `model.py`
3. **Environment vars**: Update `.env.example`

### Running Tests:

```bash
pytest
```

## 🤝 Integration Example

Frontend integration example (JavaScript):

```javascript
async function analyzeProduct(imageFile, question) {
  const formData = new FormData();
  formData.append('image', imageFile);
  formData.append('query', question);
  
  const response = await fetch('http://localhost:8000/chat', {
    method: 'POST',
    body: formData
  });
  
  const data = await response.json();
  return data.response;
}
```

## 📄 License

[Your License Here]

## 👥 Contributors

[Your Name/Team]

## 📧 Support

For issues and questions, please refer to the project documentation or contact the development team.

---

**Note**: This is a demo/development version. For production use, please integrate the actual Gemma model with vision capabilities and implement proper security measures.
