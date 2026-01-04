# Food Product Assistant API Documentation

## Overview
The Food Product Assistant API provides AI-powered food product analysis using image recognition and natural language processing. The API accepts food product images and returns structured nutritional information, ingredients, and health recommendations.

## Base URL
```
http://localhost:9001
```

## Frontend Integration
The foodproject frontend is now fully integrated with the backend API. Access the web interface at:
```
http://localhost:9001/foodproject/
```

---

## Endpoints

### 1. Image-Only Analysis (Recommended for Frontend)
**Endpoint:** `POST /analyze`

**Description:** Analyzes a food product image and returns structured JSON data. This endpoint is optimized for frontend integration as it only requires an image upload.

**Request:**
- Method: `POST`
- Content-Type: `multipart/form-data`
- Body Parameters:
  - `image` (file, required): Food product image file (JPEG, PNG)

**Example using JavaScript (Frontend):**
```javascript
const formData = new FormData();
formData.append('image', imageFile);

const response = await fetch('http://localhost:9001/analyze', {
    method: 'POST',
    body: formData
});

const result = await response.json();
```

**Example using cURL:**
```bash
curl -X POST "http://localhost:9001/analyze" \
  -H "Content-Type: multipart/form-data" \
  -F "image=@/path/to/food_image.jpg"
```

**Response Format:**
```json
{
  "success": true,
  "data": {
    "name": "Tomato Paste",
    "description": "A concentrated tomato product commonly used as a cooking ingredient to add rich tomato flavor to dishes.",
    "weight": "320 g",
    "nutrition": {
      "calories": 82,
      "carbs": 18.0,
      "protein": 4.3,
      "fats": 0.5,
      "sugar": 12.4
    },
    "ingredients": [
      "Tomatoes - 128 g",
      "Added Sugar - 64 g",
      "Garlic - 0.48 g",
      "Salt - 3.0 g"
    ],
    "healthRating": "occasional",
    "recommendation": "Consume Occasionally",
    "additionalNotes": "High sugar content. Contains preservatives.",
    "rawResponse": "Full AI response text..."
  },
  "message": "Food analysis completed successfully",
  "processing_time": 2.45,
  "timestamp": "2026-01-04T10:30:00.123456"
}
```

**Response Fields:**
- `success` (boolean): Whether the analysis was successful
- `data` (object): Structured food analysis data
  - `name` (string): Product name
  - `description` (string): Brief 1-2 sentence description of the product
  - `weight` (string): Serving size or weight
  - `nutrition` (object): Nutritional information per 100g
    - `calories` (number): Calories in kcal
    - `carbs` (number): Carbohydrates in grams
    - `protein` (number): Protein in grams
    - `fats` (number): Total fats in grams
    - `sugar` (number): Sugar in grams
  - `ingredients` (array): List of ingredients with amounts
  - `healthRating` (string): "safe" | "occasional" | "high-risk" | "unknown"
  - `recommendation` (string): Consumption recommendation
  - `additionalNotes` (string): Additional health information
  - `rawResponse` (string): Complete AI response text
- `message` (string): Status message
- `processing_time` (number): Processing time in seconds
- `timestamp` (string): ISO 8601 timestamp

**Error Response:**
```json
{
  "success": false,
  "data": null,
  "message": "Analysis failed: Invalid file type",
  "processing_time": 0.15,
  "timestamp": "2026-01-04T10:30:00.123456"
}
```

---

### 2. Chat with Image and Query
**Endpoint:** `POST /chat`

**Description:** Processes a food product image with a specific user query. Provides more flexible, conversational responses.

**Request:**
- Method: `POST`
- Content-Type: `multipart/form-data`
- Body Parameters:
  - `image` (file, required): Product image (JPEG, PNG)
  - `query` (string, required): User's question about the product

**Example:**
```bash
curl -X POST "http://localhost:9001/chat" \
  -F "image=@product.jpg" \
  -F "query=Is this product healthy for diabetics?"
```

**Response:**
```json
{
  "response": "This product contains high amounts of sugar (12.4g per 100g), which may not be suitable for diabetics...",
  "timestamp": "2026-01-04T10:30:00.123456",
  "processing_time": 2.34
}
```

---

### 3. Health Check
**Endpoint:** `GET /health`

**Description:** Check API health status and model availability.

**Example:**
```bash
curl http://localhost:9001/health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2026-01-04T10:30:00.123456",
  "model_loaded": true
}
```

---

### 4. API Statistics
**Endpoint:** `GET /stats`

**Description:** Get API usage statistics and uptime information.

**Example:**
```bash
curl http://localhost:9001/stats
```

**Response:**
```json
{
  "total_requests": 150,
  "successful_requests": 145,
  "failed_requests": 5,
  "uptime_seconds": 3600.5,
  "start_time": "2026-01-04T09:00:00.000000"
}
```

---

### 5. API Information
**Endpoint:** `GET /info`

**Description:** Get detailed API information, features, and capabilities.

**Example:**
```bash
curl http://localhost:9001/info
```

---

### 6. Root Endpoint
**Endpoint:** `GET /`

**Description:** API overview and endpoint list.

**Example:**
```bash
curl http://localhost:9001/
```

---

## Frontend Integration Guide

### HTML File Upload Example
```html
<input type="file" id="foodImage" accept="image/*">
<button onclick="analyzeFood()">Analyze</button>

<script src="app.js"></script>
<script>
async function analyzeFood() {
    const fileInput = document.getElementById('foodImage');
    const file = fileInput.files[0];
    
    if (!file) {
        alert('Please select an image');
        return;
    }
    
    try {
        // Use the helper function from app.js
        const result = await analyzeFood(file);
        console.log('Analysis result:', result);
        
        // Display results
        displayResults(result);
    } catch (error) {
        console.error('Error:', error);
        alert('Analysis failed: ' + error.message);
    }
}

function displayResults(foodData) {
    // Update your UI with the results
    document.getElementById('foodName').textContent = foodData.name;
    document.getElementById('calories').textContent = foodData.nutrition.calories;
    // ... more fields
}
</script>
```

### Using the Integrated App.js
The `app.js` file in the foodproject directory provides helper functions:

```javascript
// In your HTML file, include app.js first
<script src="app.js"></script>

// Then use the provided functions
const fileInput = document.getElementById('myFileInput');
fileInput.addEventListener('change', async (e) => {
    const file = e.target.files[0];
    
    // Analyze the food image
    const foodData = await analyzeFood(file);
    
    // The result is automatically stored in AppState
    console.log(AppState.getCurrentFood());
    
    // Show success notification
    showToast('Analysis complete!', 'success');
});
```

---

## Health Rating Values

| Rating | Description | UI Color |
|--------|-------------|----------|
| `safe` | Mostly safe for regular consumption | Green |
| `occasional` | Should be consumed in moderation | Orange |
| `high-risk` | High in unhealthy components, consume rarely | Red |
| `unknown` | Unable to determine health rating | Gray |

---

## Supported Image Formats
- JPEG (.jpg, .jpeg)
- PNG (.png)

Maximum recommended image size: 10MB

---

## Error Codes

| Status Code | Description |
|-------------|-------------|
| 200 | Success |
| 400 | Bad Request (invalid file type, missing parameters) |
| 404 | Not Found (invalid endpoint) |
| 500 | Internal Server Error (processing failed) |

---

## Rate Limiting
Currently, no rate limiting is implemented. Consider implementing rate limiting for production use.

---

## CORS Configuration
The API currently allows requests from all origins (`*`). For production, configure specific allowed origins in [main.py](main.py#L31).

---

## Running the Server

### Start the backend server:
```bash
# Using the start script
./start.sh

# Or manually
python main.py
```

The server will start on `http://localhost:9001`

### Access the frontend:
1. Open your browser
2. Navigate to `http://localhost:9001/foodproject/`
3. Upload a food product image
4. View the analysis results

---

## Environment Variables

Required environment variables (set in `.env` file):
```
GEMINI_API_KEY=your_gemini_api_key_here
MODEL_NAME=gemini-1.5-flash
USE_GPU=true
MAX_TOKENS=2048
TEMPERATURE=0.7
```

---

## Example Workflow

1. **User uploads image** on frontend (index.html)
2. **Frontend calls** `/analyze` endpoint with FormData
3. **Backend processes** image with Gemini AI model
4. **Backend returns** structured JSON response
5. **Frontend displays** results on detail.html page

---

## Interactive API Documentation

FastAPI provides interactive API documentation:
- Swagger UI: `http://localhost:9001/docs`
- ReDoc: `http://localhost:9001/redoc`

---

## Support

For issues or questions:
1. Check the API health: `GET /health`
2. Review server logs for errors
3. Verify your GEMINI_API_KEY is set correctly
4. Ensure all dependencies are installed: `pip install -r requirements.txt`
