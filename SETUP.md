# Quick Setup Guide - Food Product Assistant

## ⚡ Fast Setup (3 minutes)

### Step 1: Get Your Gemini API Key (1 min)
1. Go to: https://makersuite.google.com/app/apikey
2. Sign in with Google
3. Click "Create API Key"
4. Copy the API key

### Step 2: Configure (30 seconds)
Open the `.env` file and add your API key:
```
GEMINI_API_KEY="paste_your_key_here"
```

### Step 3: Install & Run (1-2 minutes)

**Option A - Using Script (Recommended):**
```bash
# Linux/Mac
./start.sh

# Windows
start.bat
```

**Option B - Manual:**
```bash
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
python main.py
```

### Step 4: Test It!
- Open browser: http://localhost:8000/docs
- Or open: `demo.html` in your browser
- Upload a food product image
- Ask a question like "What are the ingredients?"

## 🎮 GPU Setup (Optional - for NVIDIA GPUs)

Check if GPU is detected:
```bash
python -c "import torch; print(f'GPU: {torch.cuda.is_available()}')"
```

If you have NVIDIA GPU and want CUDA support:
```bash
# For CUDA 11.8
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118

# For CUDA 12.1
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
```

## 📝 Common Issues & Solutions

### Issue: "ModuleNotFoundError: No module named 'google.generativeai'"
**Solution:** Install dependencies
```bash
pip install -r requirements.txt
```

### Issue: "API key not configured"
**Solution:** Add your API key to `.env`:
```
GEMINI_API_KEY="your_key_here"
```

### Issue: Port 8000 already in use
**Solution:** Change port in `.env`:
```
PORT=8001
```
Then run: `python main.py`

### Issue: GPU not detected (but you have NVIDIA GPU)
**Solution:** Install PyTorch with CUDA:
```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

## 🧪 Testing

### Quick API Test:
```bash
python test_api.py
```

### Test with image:
```bash
python test_api.py --image path/to/food_image.jpg --query "What are the ingredients?"
```

### Manual cURL Test:
```bash
curl -X POST http://localhost:8000/chat \
  -F "image=@food_product.jpg" \
  -F "query=Is this vegetarian?"
```

## 📚 Next Steps

1. **Try the demo**: Open `demo.html` in your browser
2. **Read API docs**: http://localhost:8000/docs
3. **Check stats**: http://localhost:8000/stats
4. **Integrate with frontend**: See examples in README.md

## 💡 Tips

- Use **gemini-1.5-flash** for fast responses (default)
- Use **gemini-1.5-pro** for higher quality analysis
- GPU preprocessing is automatic if NVIDIA GPU is detected
- The free tier is generous for testing and development
- Images are automatically optimized to 1024x1024 for best results

## 🔗 Useful Links

- Get API Key: https://makersuite.google.com/app/apikey
- Gemini Docs: https://ai.google.dev/docs
- API Documentation: http://localhost:8000/docs (when server is running)
- Project README: README.md

## ✅ Verification Checklist

- [ ] Python 3.8+ installed
- [ ] Virtual environment created
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Gemini API key added to `.env`
- [ ] Server starts without errors (`python main.py`)
- [ ] Can access http://localhost:8000
- [ ] Can upload image and get response

---

**Need help?** Check the full README.md or the error logs in the terminal.
