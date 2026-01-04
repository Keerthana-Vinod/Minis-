"""
FastAPI Server for Food Product Assistant Chatbot
Processes product images and text queries using Gemma model
"""

from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional, Dict, Any
import time
import base64
from datetime import datetime
import uvicorn
from io import BytesIO
from PIL import Image
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Food Product Assistant API",
    description="AI-powered chatbot for food product analysis and queries",
    version="1.0.0"
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Statistics tracking
stats = {
    "total_requests": 0,
    "successful_requests": 0,
    "failed_requests": 0,
    "start_time": datetime.now().isoformat()
}

# Models
class ChatResponse(BaseModel):
    """Response model for chat endpoint"""
    response: str
    timestamp: str
    processing_time: float

class StatsResponse(BaseModel):
    """Response model for stats endpoint"""
    total_requests: int
    successful_requests: int
    failed_requests: int
    uptime_seconds: float
    start_time: str

class AnalysisResponse(BaseModel):
    """Response model for image analysis endpoint"""
    success: bool
    data: Optional[str] = None  # Raw response text for frontend parsing
    message: str
    processing_time: float
    timestamp: str

# Placeholder for Gemini model integration
from model import get_model

# Initialize model
gemma_model = get_model()  # Now uses Gemini API

# Serve the frontend at root
@app.get("/", response_class=HTMLResponse, tags=["Frontend"])
async def serve_frontend():
    """Serve the main frontend page"""
    index_path = os.path.join(os.path.dirname(__file__), "foodproject", "index.html")
    
    if not os.path.exists(index_path):
        raise HTTPException(status_code=404, detail="Frontend not found")
    
    with open(index_path, "r", encoding="utf-8") as f:
        html_content = f.read()
    
    return HTMLResponse(content=html_content)

@app.get("/api", tags=["API Info"])
async def api_info():
    """API information endpoint"""
    return {
        "message": "Food Product Assistant API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "POST /analyze": "Analyze food image and return JSON",
            "POST /chat": "Send image and text query for analysis",
            "GET /stats": "Get API statistics",
            "GET /health": "Health check endpoint",
            "GET /api": "API information"
        },
        "documentation": "/docs",
        "frontend": "/"
    }

@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "model_loaded": gemma_model.model_loaded
    }

@app.get("/test", response_class=HTMLResponse, tags=["Testing"])
async def serve_demo():
    """Serve the demo HTML page for testing the API"""
    demo_path = os.path.join(os.path.dirname(__file__), "demo.html")
    
    if not os.path.exists(demo_path):
        raise HTTPException(status_code=404, detail="Demo page not found")
    
    with open(demo_path, "r", encoding="utf-8") as f:
        html_content = f.read()
    
    return HTMLResponse(content=html_content)

@app.post("/chat", response_model=ChatResponse, tags=["Chat"])
async def chat(
    image: UploadFile = File(..., description="Product image (JPEG, PNG)"),
    query: str = Form(..., description="User's question about the product")
):
    """
    Main chat endpoint for processing product images and queries
    
    Args:
        image: Uploaded product image file
        query: User's text query about the product
        
    Returns:
        ChatResponse with AI-generated answer
    """
    start_time = time.time()
    stats["total_requests"] += 1
    
    try:
        # Validate file type
        if image.content_type not in ["image/jpeg", "image/jpg", "image/png"]:
            stats["failed_requests"] += 1
            raise HTTPException(
                status_code=400, 
                detail="Invalid file type. Only JPEG and PNG images are supported."
            )
        
        # Read and process image
        logger.info(f"Processing image: {image.filename}, Query: {query[:50]}...")
        
        image_data = await image.read()
        pil_image = Image.open(BytesIO(image_data))
        
        # Convert RGBA to RGB if necessary
        if pil_image.mode == 'RGBA':
            pil_image = pil_image.convert('RGB')
        
        # Process with Gemma model
        response_text = await gemma_model.process_image_and_text(pil_image, query)
        
        processing_time = time.time() - start_time
        stats["successful_requests"] += 1
        
        logger.info(f"Request processed successfully in {processing_time:.2f}s")
        
        return ChatResponse(
            response=response_text,
            timestamp=datetime.now().isoformat(),
            processing_time=processing_time
        )
        
    except HTTPException:
        raise
    except Exception as e:
        stats["failed_requests"] += 1
        logger.error(f"Error processing request: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/stats", response_model=StatsResponse, tags=["Statistics"])
async def get_stats():
    """
    Get API usage statistics
    
    Returns:
        Statistics including request counts and uptime
    """
    start_time_obj = datetime.fromisoformat(stats["start_time"])
    uptime_seconds = (datetime.now() - start_time_obj).total_seconds()
    
    return StatsResponse(
        total_requests=stats["total_requests"],
        successful_requests=stats["successful_requests"],
        failed_requests=stats["failed_requests"],
        uptime_seconds=uptime_seconds,
        start_time=stats["start_time"]
    )

@app.post("/analyze", response_model=AnalysisResponse, tags=["Analysis"])
async def analyze_food_image(
    image: UploadFile = File(..., description="Food product image (JPEG, PNG)")
):
    """
    Analyze food product from image only - returns structured JSON
    
    Args:
        image: Uploaded food product image file
        
    Returns:
        AnalysisResponse with structured food analysis data
    """

    print(f"🔍 RECEIVED ANALYZE REQUEST for file: {image.filename}")
    start_time = time.time()
    stats["total_requests"] += 1
    
    try:
        # Validate file type
        if image.content_type not in ["image/jpeg", "image/jpg", "image/png"]:
            stats["failed_requests"] += 1
            raise HTTPException(
                status_code=400, 
                detail="Invalid file type. Only JPEG and PNG images are supported."
            )
        
        # Read and process image
        logger.info(f"Analyzing image: {image.filename}")
        
        image_data = await image.read()
        pil_image = Image.open(BytesIO(image_data))
        
        # Convert RGBA to RGB if necessary
        if pil_image.mode == 'RGBA':
            pil_image = pil_image.convert('RGB')
        
        # Create a comprehensive analysis query
        analysis_query = """Analyze this food product image and provide detailed information in VALID JSON format only. Do NOT include any text before or after the JSON.

Return ONLY a JSON object with this exact structure:
{
  "productName": "Exact brand and product name (e.g., Coca-Cola Classic)",
  "description": "Critical health analysis: Explain how good or bad this product is for health, including specific health risks, nutritional concerns, and dietary impact. Be honest about negative effects like sugar content, additives, and long-term health implications.",
  "weight": "serving size with units (e.g., 355ml)",
  "nutrition": {
    "calories": 140,
    "carbs": 39,
    "protein": 0,
    "fats": 0,
    "sugar": 39,
    "fiber": 0,
    "sodium": 45
  },
  "ingredients": ["carbonated water", "high fructose corn syrup", "caramel color", "phosphoric acid", "natural flavors", "caffeine"],
  "healthRating": "high_risk",
  "recommendation": "Avoid regular consumption due to high sugar and potential health risks",
  "additionalNotes": "Contains artificial colors, high caffeine, contributes to obesity and dental decay"
}

CRITICAL REQUIREMENTS:
- Return ONLY valid JSON, no markdown, no extra text
- Description must be a critical health analysis, not product marketing
- Be honest about health risks and negative nutritional impacts
- Use exact brand names and accurate nutritional data
- Health rating options: "safe", "occasional", "high_risk"
- Recommendation should reflect actual health impact"""
        
        # Process with Gemini model
        response_text = await gemma_model.process_image_and_text(pil_image, analysis_query)
        
        # Debug: Print the raw response
        print(f"DEBUG: Raw AI response ({len(response_text)} chars):")
        print(response_text)
        print("=" * 50)
        
        # Return raw response text for frontend parsing
        analysis_data = response_text
        
        processing_time = time.time() - start_time
        stats["successful_requests"] += 1
        
        logger.info(f"Image analysis completed successfully in {processing_time:.2f}s")
        
        print(f"📤 SENDING RESPONSE: success=True, data_length={len(analysis_data)}, message='Food analysis completed successfully'")
        
        return AnalysisResponse(
            success=True,
            data=analysis_data,  # Raw response text
            message="Food analysis completed successfully",
            processing_time=processing_time,
            timestamp=datetime.now().isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        stats["failed_requests"] += 1
        logger.error(f"Error analyzing image: {str(e)}")
        return AnalysisResponse(
            success=False,
            data=None,
            message=f"Analysis failed: {str(e)}",
            processing_time=time.time() - start_time,
            timestamp=datetime.now().isoformat()
        )

def parse_json_from_markdown(response_text: str) -> Dict[str, Any]:
    """
    Extract and parse JSON from markdown code blocks
    
    Args:
        response_text: Raw text response that may contain markdown-wrapped JSON
        
    Returns:
        Parsed JSON dictionary
    """
    import json
    import re
    
    # Default fallback data
    default_data = {
        "name": "Unknown Product",
        "description": "",
        "weight": "N/A",
        "nutrition": {
            "calories": 0,
            "carbs": 0,
            "protein": 0,
            "fats": 0,
            "sugar": 0
        },
        "ingredients": [],
        "healthRating": "unknown",
        "recommendation": "Consult nutritionist",
        "additionalNotes": "",
        "rawResponse": response_text
    }
    
    try:
        # Look for JSON in markdown code blocks
        json_pattern = r'```(?:json)?\s*\n(.*?)\n```'
        match = re.search(json_pattern, response_text, re.DOTALL)
        
        if match:
            json_str = match.group(1).strip()
            return json.loads(json_str)
        
        # If no markdown blocks, try to find JSON directly
        # Look for opening brace and closing brace
        start_idx = response_text.find('{')
        end_idx = response_text.rfind('}')
        
        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
            json_str = response_text[start_idx:end_idx+1]
            return json.loads(json_str)
        
        # If no JSON found, return default with raw response
        logger.warning(f"No JSON found in response, using default data. Response: {response_text[:200]}...")
        return default_data
        
    except json.JSONDecodeError as e:
        logger.error(f"JSON parsing failed: {e}. Response: {response_text[:200]}...")
        return default_data
    except Exception as e:
        logger.error(f"Unexpected error parsing JSON: {e}")
        return default_data

def parse_food_analysis(response_text: str) -> Dict[str, Any]:
    """
    Parse the AI response into structured JSON format
    
    Args:
        response_text: Raw text response from the AI model
        
    Returns:
        Structured dictionary with food analysis data
    """
    # Initialize default structure
    data = {
        "name": "Unknown Product",
        "description": "",
        "weight": "N/A",
        "nutrition": {
            "calories": 0,
            "carbs": 0,
            "protein": 0,
            "fats": 0,
            "sugar": 0
        },
        "ingredients": [],
        "healthRating": "unknown",
        "recommendation": "Consult nutritionist",
        "additionalNotes": "",
        "rawResponse": response_text
    }
    
    try:
        lines = response_text.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Extract product name
            if line.lower().startswith('product name:'):
                data["name"] = line.split(':', 1)[1].strip()
                
            # Extract description
            elif line.lower().startswith('description:'):
                data["description"] = line.split(':', 1)[1].strip()
                
            # Extract weight
            elif line.lower().startswith('weight') or line.lower().startswith('serving size'):
                data["weight"] = line.split(':', 1)[1].strip() if ':' in line else "N/A"
                
            # Extract nutritional info
            elif 'calories' in line.lower() and ':' in line:
                try:
                    cal_str = line.split(':')[1].strip().split()[0]
                    data["nutrition"]["calories"] = float(cal_str.replace(',', ''))
                except:
                    pass
                    
            elif 'carbohydrate' in line.lower() and ':' in line:
                try:
                    carb_str = line.split(':')[1].strip().split()[0]
                    data["nutrition"]["carbs"] = float(carb_str.replace(',', ''))
                except:
                    pass
                    
            elif 'protein' in line.lower() and ':' in line:
                try:
                    prot_str = line.split(':')[1].strip().split()[0]
                    data["nutrition"]["protein"] = float(prot_str.replace(',', ''))
                except:
                    pass
                    
            elif 'fat' in line.lower() and ':' in line and 'saturated' not in line.lower():
                try:
                    fat_str = line.split(':')[1].strip().split()[0]
                    data["nutrition"]["fats"] = float(fat_str.replace(',', ''))
                except:
                    pass
                    
            elif 'sugar' in line.lower() and ':' in line:
                try:
                    sugar_str = line.split(':')[1].strip().split()[0]
                    data["nutrition"]["sugar"] = float(sugar_str.replace(',', ''))
                except:
                    pass
                    
            # Extract health rating
            elif line.lower().startswith('health rating:'):
                rating = line.split(':', 1)[1].strip().lower()
                if 'safe' in rating or 'green' in rating:
                    data["healthRating"] = "safe"
                elif 'occasional' in rating or 'moderate' in rating:
                    data["healthRating"] = "occasional"
                elif 'risk' in rating or 'red' in rating:
                    data["healthRating"] = "high-risk"
                    
            # Extract recommendation
            elif line.lower().startswith('recommendation:'):
                data["recommendation"] = line.split(':', 1)[1].strip()
                
            # Extract ingredients section
            elif line.lower().startswith('ingredients'):
                current_section = 'ingredients'
            elif current_section == 'ingredients' and line and not line.lower().startswith('health') and not line.lower().startswith('recommendation'):
                # Clean up ingredient line
                ingredient = line.lstrip('-•*').strip()
                if ingredient and len(ingredient) > 2:
                    data["ingredients"].append(ingredient)
                    
            # Additional notes
            elif line.lower().startswith('additional notes:'):
                data["additionalNotes"] = line.split(':', 1)[1].strip()
                
    except Exception as e:
        logger.warning(f"Error parsing analysis: {str(e)}")
        
    return data

@app.get("/info", tags=["Information"])
async def get_info():
    """Get detailed API information"""
    return {
        "api_name": "Food Product Assistant",
        "description": "AI-powered assistant for analyzing food products from images",
        "features": [
            "Product image analysis",
            "Ingredient identification",
            "Nutritional information extraction",
            "Allergen detection",
            "Dietary recommendations"
        ],
        "supported_formats": ["JPEG", "PNG"],
        "model": "Gemma (Vision-Language Model)",
        "version": "1.0.0"
    }

# Mount static files for CSS, JS, and other assets
app.mount("/static", StaticFiles(directory="foodproject"), name="static")

@app.get("/")
async def read_root():
    return FileResponse("foodproject/index.html")

@app.get("/app.js")
async def read_app_js():
    return FileResponse("foodproject/app.js", media_type="application/javascript")

@app.get("/styles.css")
async def read_styles():
    return FileResponse("foodproject/styles.css", media_type="text/css")

@app.get("/detail.html")
async def read_detail():
    return FileResponse("foodproject/detail.html")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=9001,
        reload=True,
        log_level="info"
    )
