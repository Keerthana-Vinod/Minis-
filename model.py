"""
Gemini API Integration Module
Handles image processing and API calls to Google Gemini for food product analysis
Uses local GPU-accelerated image preprocessing
"""

import google.generativeai as genai
from PIL import Image
import logging
from typing import Optional
import os
import torch
import numpy as np
import torchvision.transforms as transforms
from torchvision.models import resnet50, ResNet50_Weights
import torch.nn.functional as F
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class GeminiVisionModel:
    """
    Gemini Vision API for food product analysis
    Uses Google Gemini API with local GPU-accelerated image preprocessing
    """
    
    def __init__(self):
        """Initialize the Gemini API client"""
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.model_name = os.getenv("MODEL_NAME", "gemini-1.5-flash")
        self.use_gpu = torch.cuda.is_available() and os.getenv("USE_GPU", "true").lower() == "true"
        self.device = "cuda" if self.use_gpu else "cpu"
        self.max_tokens = int(os.getenv("MAX_TOKENS", "2048"))
        self.temperature = float(os.getenv("TEMPERATURE", "0.7"))
        
        self.model = None
        self.gemma_model = None
        self.model_loaded = False
        self.gemma_loaded = False
        
        # Local image classification model for hybrid approach
        self.local_vision_model = None
        self.use_hybrid_mode = os.getenv("USE_HYBRID_MODE", "true").lower() == "true"
        
        logger.info(f"Initializing Gemini API with model: {self.model_name}")
        logger.info(f"GPU Available: {self.use_gpu} | Device: {self.device}")
        if self.use_gpu:
            gpu_name = torch.cuda.get_device_name(0)
            logger.info(f"GPU: {gpu_name}")
        logger.info(f"Hybrid Mode (Local Vision + Gemma Text): {self.use_hybrid_mode}")
        
        # Setup image preprocessing transforms (GPU-accelerated if available)
        self.image_transforms = transforms.Compose([
            transforms.Resize((1024, 1024)),  # Optimal size for Gemini
            transforms.ToTensor(),
        ])
        
        try:
            self._configure_api()
        except Exception as e:
            logger.error(f"Failed to configure Gemini API: {str(e)}")
            logger.warning("Attempting to configure Gemma fallback model...")
            try:
                self._configure_gemma_fallback()
            except Exception as gemma_error:
                logger.error(f"Failed to configure Gemma fallback: {str(gemma_error)}")
                logger.warning("Running in basic demo mode")
        
        # Always try to load Gemma for hybrid mode, even if Gemini works
        if self.use_hybrid_mode and not self.gemma_loaded:
            try:
                logger.info("Loading Gemma model for hybrid mode text generation...")
                self._configure_gemma_fallback()
            except Exception as e:
                logger.warning(f"Could not load Gemma for hybrid mode: {e}")
        
        # Try to load local vision model for hybrid mode
        if self.use_hybrid_mode:
            try:
                self._load_local_vision_model()
            except Exception as e:
                logger.warning(f"Could not load local vision model: {e}")
    
    def _load_local_vision_model(self):
        """Load a local vision model for image analysis"""
        try:
            logger.info("Loading local ResNet50 vision model...")
            self.local_vision_model = resnet50(weights=ResNet50_Weights.IMAGENET1K_V2)
            self.local_vision_model.eval()
            if self.use_gpu:
                self.local_vision_model = self.local_vision_model.to(self.device)
            
            # Load ImageNet class labels
            import urllib.request
            import json
            
            url = "https://raw.githubusercontent.com/anishathalye/imagenet-simple-labels/master/imagenet-simple-labels.json"
            with urllib.request.urlopen(url) as f:
                self.imagenet_labels = json.load(f)
            
            logger.info("✅ Local vision model loaded successfully")
        except Exception as e:
            logger.warning(f"Could not load local vision model: {e}")
            self.local_vision_model = None
    
    def _configure_api(self):
        """Configure the Gemini API client"""
        try:
            if not self.api_key:
                logger.warning("No GEMINI_API_KEY found in environment variables")
                return
            
            # Configure Gemini API
            genai.configure(api_key=self.api_key)
            
            # List available models with vision support
            print(f"\n{'='*60}")
            print("📋 Checking available models with vision support...")
            print(f"{'='*60}")
            
            available_vision_models = []
            try:
                for m in genai.list_models():
                    if 'generateContent' in m.supported_generation_methods:
                        # Check if model supports vision (has vision or image in name, or is gemini-pro-vision)
                        model_name_lower = m.name.lower()
                        supports_vision = (
                            'vision' in model_name_lower or 
                            'image' in model_name_lower or
                            'flash' in model_name_lower or
                            'pro' in model_name_lower or
                            'exp' in model_name_lower
                        )
                        # Exclude text-only models like gemma
                        is_text_only = 'gemma' in model_name_lower and 'image' not in model_name_lower
                        
                        if supports_vision and not is_text_only:
                            available_vision_models.append(m.name)
                            print(f"  ✓ {m.name}")
            except Exception as e:
                logger.warning(f"Could not list models: {e}")
            
            print(f"{'='*60}\n")
            
            # Try to find the best available model for vision
            # Priority: user's choice -> fast models (flash/lite) -> pro models
            model_to_use = None
            
            # Check if user's specified model is available
            user_model = f"models/{self.model_name}"
            if user_model in available_vision_models:
                model_to_use = self.model_name
                print(f"✅ Using user-specified model: {model_to_use}")
            else:
                # Prefer fast, free-tier friendly models
                flash_candidates = [m for m in available_vision_models if 'flash' in m.lower() or 'lite' in m.lower()]
                if flash_candidates:
                    # Prefer simpler flash models first
                    for candidate in flash_candidates:
                        if 'gemini-2.0-flash' in candidate or 'flash-latest' in candidate:
                            model_to_use = candidate.replace('models/', '')
                            break
                    if not model_to_use:
                        model_to_use = flash_candidates[0].replace('models/', '')
                    print(f"✅ Using fast model (best for free tier): {model_to_use}")
                else:
                    # Fall back to any available vision model
                    if available_vision_models:
                        model_to_use = available_vision_models[0].replace('models/', '')
                        print(f"✅ Using model: {model_to_use}")
            
            if not model_to_use:
                raise Exception("No compatible models found")
            
            # Initialize model
            logger.info(f"Configuring model: {model_to_use}")
            self.model = genai.GenerativeModel(model_to_use)
            self.model_name = model_to_use
            
            self.model_loaded = True
            logger.info("API configured successfully!")
            print(f"🎉 Model loaded successfully: {model_to_use}\n")
            
        except Exception as e:
            logger.error(f"Error configuring API: {str(e)}") 
            raise
    
    def _configure_gemma_fallback(self):
        """Configure Gemma model as fallback when Gemini is not available"""
        try:
            if not self.api_key:
                logger.warning("No API key available for Gemma fallback")
                return
            
            # Configure API if not already done
            genai.configure(api_key=self.api_key)
            
            # Try Gemma models (text-only, but can work with image descriptions)
            gemma_models = ["gemma-3-12b-it", "gemma-3-4b-it", "gemma-3-1b-it"]
            
            for model_name in gemma_models:
                try:
                    logger.info(f"Attempting to configure Gemma model: {model_name}")
                    self.gemma_model = genai.GenerativeModel(model_name)
                    self.gemma_loaded = True
                    logger.info(f"Gemma fallback model configured: {model_name}")
                    return
                except Exception as e:
                    logger.warning(f"Could not load {model_name}: {str(e)}")
                    continue
            
            logger.warning("No Gemma models available")
            
        except Exception as e:
            logger.error(f"Error configuring Gemma fallback: {str(e)}")
            raise
    
    def preprocess_image(self, image: Image.Image) -> Image.Image:
        """
        Preprocess image using GPU acceleration if available
        
        Args:
            image: PIL Image object
            
        Returns:
            Preprocessed PIL Image
        """
        try:
            # Convert to RGB if needed
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Simple resize for compatibility
            image = image.resize((1024, 1024), Image.Resampling.LANCZOS)
            
            return image
            
        except Exception as e:
            logger.warning(f"Image preprocessing failed: {str(e)}")
            if image.mode != 'RGB':
                image = image.convert('RGB')
            # Fallback to simple resize
            return image.resize((1024, 1024), Image.Resampling.LANCZOS)
    
    def analyze_image_locally(self, image: Image.Image) -> dict:
        """
        Analyze image using local vision model
        
        Args:
            image: PIL Image object
            
        Returns:
            Dictionary with image analysis results
        """
        if not self.local_vision_model:
            return {"detected_objects": [], "confidence": 0, "description": "Unable to analyze image locally"}
        
        try:
            logger.info("🔍 Analyzing image with local ResNet50 model...")
            
            # Convert PIL image to RGB if needed
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Resize and crop manually (equivalent to Resize(256), CenterCrop(224))
            width, height = image.size
            # Resize to 256 on shortest side
            if width < height:
                new_width = 256
                new_height = int(height * (256 / width))
            else:
                new_height = 256
                new_width = int(width * (256 / height))
            
            image = image.resize((new_width, new_height), Image.Resampling.BILINEAR)
            
            # Center crop to 224x224
            left = (new_width - 224) // 2
            top = (new_height - 224) // 2
            right = left + 224
            bottom = top + 224
            image = image.crop((left, top, right, bottom))
            
            # Convert to numpy array and normalize manually
            img_array = np.array(image, dtype=np.float32) / 255.0
            
            # Apply ImageNet normalization: mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]
            mean = np.array([0.485, 0.456, 0.406], dtype=np.float32)
            std = np.array([0.229, 0.224, 0.225], dtype=np.float32)
            img_array = (img_array - mean) / std
            
            # Convert to CHW format (channels, height, width)
            img_array = np.transpose(img_array, (2, 0, 1))
            
            # Convert to torch tensor
            input_tensor = torch.from_numpy(img_array).unsqueeze(0)
            
            if self.use_gpu:
                input_tensor = input_tensor.to(self.device)
            
            # Get predictions
            with torch.no_grad():
                output = self.local_vision_model(input_tensor)
            
            # Get top 5 predictions
            probabilities = F.softmax(output[0], dim=0)
            top5_prob, top5_catid = torch.topk(probabilities, 5)
            
            detected_objects = []
            for i in range(top5_prob.size(0)):
                confidence = top5_prob[i].item()
                if confidence > 0.01:  # Only include if > 1% confidence
                    label = self.imagenet_labels[top5_catid[i].item()] if hasattr(self, 'imagenet_labels') else f"class_{top5_catid[i].item()}"
                    detected_objects.append({
                        "label": label,
                        "confidence": confidence
                    })
            
            # Create description
            if detected_objects:
                top_label = detected_objects[0]["label"]
                top_conf = detected_objects[0]["confidence"] * 100
                description = f"The image appears to show {top_label} (confidence: {top_conf:.1f}%)"
                if len(detected_objects) > 1:
                    other_labels = ", ".join([obj["label"] for obj in detected_objects[1:3]])
                    description += f". Other possibilities: {other_labels}"
            else:
                description = "Could not identify objects in the image"
            
            print(f"  ✓ Local analysis: {description}")
            
            return {
                "detected_objects": detected_objects,
                "confidence": detected_objects[0]["confidence"] if detected_objects else 0,
                "description": description
            }
            
        except Exception as e:
            logger.error(f"Error in local image analysis: {e}")
            return {"detected_objects": [], "confidence": 0, "description": f"Error analyzing image: {str(e)}"}
    
    def create_prompt(self, query: str) -> str:
        """
        Create a structured prompt for the model
        
        Args:
            query: User's question
            
        Returns:
            Formatted prompt string
        """
        prompt = f"""You are an expert food product analysis assistant. Analyze the food product image carefully and answer the user's question with detailed, accurate information.

🔍 Analysis Focus:
- Product identification and brand recognition
- Ingredients list and composition
- Nutritional information (calories, macros, vitamins)
- Allergen identification and warnings
- Dietary classifications (vegetarian, vegan, gluten-free, organic, etc.)
- Health considerations and recommendations
- Storage and usage instructions

❓ User's Question: {query}

📝 IMPORTANT: Respond with VALID JSON only. Do NOT include any text before or after the JSON. Return a JSON object with food analysis data including productName, description (critical health analysis), nutrition, ingredients, healthRating, and recommendation."""
        return prompt
    
    async def process_image_and_text(self, image: Image.Image, query: str) -> str:
        """
        Process image and text query using Gemini API
        
        Args:
            image: PIL Image object of the food product
            query: User's text query
            
        Returns:
            Model's response as string
        """
        try:
            if not self.model_loaded:
                print("\n⚠️  LLM NOT LOADED - Using fallback/demo mode")
                return self._generate_mock_response(image, query)
            
            print(f"\n{'='*60}")
            print(f"🤖 INVOKING GEMINI LLM: {self.model_name}")
            print(f"{'='*60}")
            print(f"📝 Query: {query[:100]}...")
            print(f"🖼️  Image: {image.size[0]}x{image.size[1]} pixels")
            
            # Preprocess image with GPU acceleration
            logger.info(f"Preprocessing image on {self.device}...")
            processed_image = self.preprocess_image(image)
            
            # Create prompt
            prompt = self.create_prompt(query)
            
            # Generate response using Gemini API
            print(f"⏳ Sending request to Gemini API...")
            logger.info("Sending request to Gemini API...")
            response = self.model.generate_content(
                [prompt, processed_image],
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=self.max_tokens,
                    temperature=self.temperature,
                )
            )
            
            # Extract text from response
            response_text = response.text.strip()
            
            print(f"✅ Response received from Gemini ({len(response_text)} chars)")
            print(f"{'='*60}\n")
            logger.info("Response received successfully from Gemini API")
            return response_text
            
        except Exception as e:
            print(f"\n❌ GEMINI API ERROR: {str(e)}")
            logger.error(f"Error during Gemini API call: {str(e)}")
            
            # Check if it's a quota error and we can use hybrid mode
            if "quota" in str(e).lower() or "429" in str(e):
                print("\n💡 QUOTA EXCEEDED - Switching to HYBRID MODE (Local Vision + Gemma Text)")
                if self.use_hybrid_mode and (self.local_vision_model or self.gemma_loaded):
                    return await self._hybrid_analysis(image, query)
            
            if "API_KEY" in str(e).upper():
                logger.error("Please check your GEMINI_API_KEY in .env file")
            return self._generate_mock_response(image, query)
    
    async def _hybrid_analysis(self, image: Image.Image, query: str) -> str:
        """
        Hybrid analysis: Local vision model + Gemma text generation
        
        Args:
            image: PIL Image object
            query: User's text query
            
        Returns:
            Analysis response string
        """
        try:
            # Step 1: Analyze image locally
            local_analysis = self.analyze_image_locally(image)
            
            # Step 2: Create detailed prompt for Gemma with local analysis results
            if self.gemma_loaded and self.gemma_model:
                print(f"\n{'='*60}")
                print(f"🤖 HYBRID MODE: Local Vision → Gemma Text Generation")
                print(f"{'='*60}")
                
                hybrid_prompt = f"""Based on local image analysis, the image shows: {local_analysis['description']}

User's Original Question: {query}

You are an expert food product analyst. Based on the local vision analysis above, identify the SPECIFIC food product shown in the image. Look for:

1. BRAND NAME: Identify the exact brand (Coca-Cola, Pepsi-Cola, Sprite, Fanta, Dr Pepper, etc.)
2. PRODUCT NAME: The specific product variant (Coke, Diet Coke, Coke Zero, Pepsi, Diet Pepsi, etc.)
3. PACKAGE TYPE: Bottle, can, box, etc. and any size/color information
4. FLAVOR/VARIANT: Regular, diet, zero, cherry, vanilla, etc.

IMPORTANT BRAND IDENTIFICATION:
- Red cans/bottles with white text: Coca-Cola products
- Blue cans/bottles with white text: Pepsi-Cola products  
- Green cans/bottles: Sprite products
- Orange cans/bottles: Fanta products
- Brown cans/bottles: Dr Pepper products

OUTPUT FORMAT: Return ONLY a JSON object with the analysis data (no extra text before or after the JSON).

JSON Structure:
{{
  "productName": "Exact brand and product name (e.g., Coca-Cola Classic)",
  "description": "Critical health analysis: This product contains high amounts of sugar and artificial additives that can contribute to obesity, diabetes, and dental decay. The phosphoric acid and caffeine content may affect bone health and cause dependency. Not recommended for regular consumption.",
  "weight": "serving size with units (e.g., 355ml)",
  "nutrition": {{
    "calories": 140,
    "carbs": 39,
    "protein": 0,
    "fats": 0,
    "sugar": 39,
    "fiber": 0,
    "sodium": 45
  }},
  "ingredients": ["carbonated water", "high fructose corn syrup", "caramel color", "phosphoric acid", "natural flavors", "caffeine"],
  "healthRating": "high_risk",
  "recommendation": "Avoid regular consumption due to high sugar content and potential health risks",
  "additionalNotes": "Contains artificial colors, high caffeine, contributes to obesity and dental decay"
}}

CRITICAL: 
- Return ONLY valid JSON, no markdown code blocks, no extra text
- Description must be a critical health analysis focusing on risks and negative impacts
- Use your knowledge of actual food products to identify the EXACT brand and model
- Be honest about health risks - do NOT promote unhealthy products"""
                
                print(f"⏳ Generating detailed product analysis with Gemma...")
                logger.info("🤖 INVOKING GEMMA LLM for detailed analysis")
                response = self.gemma_model.generate_content(
                    hybrid_prompt,
                    generation_config=genai.types.GenerationConfig(
                        max_output_tokens=2048,
                        temperature=0.3,  # Lower temperature for more accurate product identification
                    )
                )
                
                response_text = response.text.strip()
                print(f"✅ Detailed analysis generated ({len(response_text)} chars)")
                print(f"{'='*60}\n")
                
                return response_text
            else:
                # Fallback to basic response with local analysis
                logger.warning("Gemma model not available for hybrid mode - using basic analysis")
                return f"""⚠️ HYBRID MODE (Limited Analysis - Gemma Unavailable)

**Local Vision Analysis:**
{local_analysis['description']}

**Detected Objects:**
""" + "\n".join([f"- {obj['label']}: {obj['confidence']*100:.1f}%" for obj in local_analysis['detected_objects']]) + f"""

**Query:** {query}

**Note:** For accurate brand identification and detailed nutritional information, please ensure Gemma model is properly configured. The analysis above is based on general object detection only.

**Recommendation:** Install/configure Gemma model for complete food product analysis including specific brand identification, accurate nutritional data, and health recommendations."""
                
        except Exception as e:
            logger.error(f"Hybrid analysis failed: {e}")
            return self._generate_mock_response(image, query)
    
    def _generate_mock_response(self, image: Image.Image, query: str) -> str:
        """
        Generate response using Gemma fallback model or basic demo
        
        Args:
            image: PIL Image object
            query: User's text query
            
        Returns:
            AI-generated or demo response string
        """
        # Try to use Gemma fallback model
        if self.gemma_loaded and self.gemma_model:
            try:
                print(f"\n{'='*60}")
                print(f"🤖 INVOKING GEMMA FALLBACK LLM")
                print(f"{'='*60}")
                logger.info("Using Gemma fallback model for response...")
                
                # Preprocess image
                processed_image = self.preprocess_image(image)
                
                # Create focused prompt for Gemma
                gemma_prompt = f"""You are a food product analysis AI assistant. Analyze this food product image and provide information in VALID JSON format only.

User Question: {query}

Return ONLY a JSON object with this exact structure:
{{
  "productName": "Exact product name and brand",
  "description": "Critical health analysis: Explain the health impact, risks, and nutritional concerns of this product. Be honest about negative effects.",
  "weight": "serving size",
  "nutrition": {{
    "calories": 0,
    "carbs": 0,
    "protein": 0,
    "fats": 0,
    "sugar": 0
  }},
  "ingredients": ["list", "of", "ingredients"],
  "healthRating": "high_risk",
  "recommendation": "Avoid due to health concerns",
  "additionalNotes": "Health warnings and concerns"
}}

CRITICAL: Return ONLY valid JSON, no extra text. Description must be a critical health analysis, not promotional."""
                
                # Generate with Gemma
                response = self.gemma_model.generate_content(
                    [gemma_prompt, processed_image],
                    generation_config=genai.types.GenerationConfig(
                        max_output_tokens=2048,
                        temperature=0.7,
                    )
                )
                
                response_text = response.text.strip()
                print(f"✅ Response received from Gemma ({len(response_text)} chars)")
                print(f"{'='*60}\n")
                logger.info("Response generated successfully with Gemma fallback")
                
                # Return JSON directly (no extra headers for JSON responses)
                return response_text
                
            except Exception as e:
                print(f"❌ Gemma fallback failed: {str(e)}")
                logger.error(f"Gemma fallback failed: {str(e)}")
                # Continue to basic demo response below
        
        # Basic demo response when no models available
        print("\n⚠️  NO LLM AVAILABLE - Returning demo response\n")
        width, height = image.size
        format_type = image.format or "Unknown"
        gpu_info = f"GPU: {torch.cuda.get_device_name(0)}" if self.use_gpu else "Device: CPU"
        
        return f"""Food Product Analysis (Demo Mode)

🖼️ Image Information:
- Dimensions: {width}x{height} pixels
- Format: {format_type}
- Processing Device: {gpu_info}

❓ Your Question: {query}

⚠️ No AI Model Available:
The system needs an API key to provide AI-powered analysis.

🔑 Setup Instructions:
1. Get a Gemini API key: https://makersuite.google.com/app/apikey
2. Add to .env file: GEMINI_API_KEY=your_key_here
3. Restart the server

📋 With API configured, you'll get:
✓ Product identification and brand recognition
✓ Complete ingredients analysis
✓ Nutritional breakdown
✓ Allergen detection
✓ Dietary classifications (vegan, gluten-free, etc.)
✓ Health recommendations
✓ Storage and usage instructions

GPU Status: {"✅ Enabled" if self.use_gpu else "❌ Disabled"}"""

# Singleton instance
_model_instance: Optional[GeminiVisionModel] = None

def get_model() -> GeminiVisionModel:
    """Get or create the model singleton instance"""
    global _model_instance
    if _model_instance is None:
        _model_instance = GeminiVisionModel()
    return _model_instance
