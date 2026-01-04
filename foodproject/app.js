// Food Analysis App - Main JavaScript File
// Backend API Configuration
const API_CONFIG = {
    baseURL: window.location.origin, // Automatically uses current server
    endpoints: {
        analyze: '/analyze',
        chat: '/chat',
        health: '/health'
    }
};

// Global state management
const AppState = {
    currentFood: null,
    uploadedImage: null,
    analysisHistory: [],
    
    setCurrentFood(food) {
        console.log('AppState.setCurrentFood called with:', food);
        console.log('Food name:', food.name);
        console.log('Food description:', food.description);
        this.currentFood = food;
        try {
            localStorage.setItem('currentFood', JSON.stringify(food));
            console.log('Data stored in localStorage successfully');
        } catch (e) {
            console.error('Failed to store in localStorage:', e);
        }
    },
    
    getCurrentFood() {
        if (!this.currentFood) {
            try {
                const stored = localStorage.getItem('currentFood');
                console.log('Retrieved from localStorage:', stored ? stored.substring(0, 200) + '...' : 'null');
                this.currentFood = stored ? JSON.parse(stored) : null;
                console.log('Parsed currentFood:', this.currentFood);
            } catch (e) {
                console.error('Failed to parse from localStorage:', e);
                this.currentFood = null;
            }
        }
        console.log('Returning currentFood:', this.currentFood);
        return this.currentFood;
    },
    
    addToHistory(food) {
        this.analysisHistory.unshift(food);
        if (this.analysisHistory.length > 10) {
            this.analysisHistory.pop();
        }
        localStorage.setItem('analysisHistory', JSON.stringify(this.analysisHistory));
    },
    
    getHistory() {
        if (this.analysisHistory.length === 0) {
            const stored = localStorage.getItem('analysisHistory');
            this.analysisHistory = stored ? JSON.parse(stored) : [];
        }
        return this.analysisHistory;
    }
};

// Food database - Sample data
const FoodDatabase = {
    'fried-chicken': {
        name: 'Fried Chicken',
        emoji: '🍗',
        weight: '350 g',
        nutrition: {
            carbs: 6.3,
            fats: 41.5,
            sugar: 2.7,
            calories: 551,
            protein: 35.2
        },
        ingredients: [
            { name: 'Chicken', icon: '🍗', amount: '250 g' },
            { name: 'Tomatoes', icon: '🍅', amount: '128 g' },
            { name: 'Added Sugar', icon: '🍬', amount: '6.48 g' },
            { name: 'Garlic', icon: '🧄', amount: '0.408 g' },
            { name: 'Salt', icon: '🧂', amount: '0.22 g' },
            { name: 'Other ingredients', icon: '📦', amount: '486 g' }
        ],
        healthRating: 'high-risk',
        recommendation: 'Consume Rarely'
    },
    'tomato-paste': {
        name: 'Tomato Paste',
        emoji: '🍅',
        weight: '320 g',
        nutrition: {
            carbs: 18,
            fats: 0.5,
            sugar: 12.4,
            calories: 82,
            protein: 4.3
        },
        ingredients: [
            { name: 'Tomatoes', icon: '🍅', amount: '128 g' },
            { name: 'Added Sugar', icon: '🍬', amount: '64 g' },
            { name: 'Garlic', icon: '🧄', amount: '0.48 g' },
            { name: 'Salt', icon: '🧂', amount: '3.0 g' },
            { name: 'Other Ingredients', icon: '🟢', amount: '48 g' }
        ],
        healthRating: 'occasional',
        recommendation: 'Consume Occasionally'
    },
    'muesli-bar': {
        name: 'Muesli Bar',
        emoji: '🍪',
        weight: '50 g',
        nutrition: {
            carbs: 45,
            fats: 12,
            sugar: 25,
            calories: 180,
            protein: 5
        },
        ingredients: [
            { name: 'Oats', icon: '🌾', amount: '20 g' },
            { name: 'Honey', icon: '🍯', amount: '10 g' },
            { name: 'Nuts', icon: '🥜', amount: '8 g' },
            { name: 'Dried Fruits', icon: '🍇', amount: '12 g' }
        ],
        healthRating: 'occasional',
        recommendation: 'Consume Occasionally'
    },
    'oatmeal': {
        name: 'Oatmeal',
        emoji: '🌾',
        weight: '350 g',
        nutrition: {
            carbs: 58,
            fats: 7,
            sugar: 1,
            calories: 389,
            protein: 16.9
        },
        ingredients: [
            { name: 'Oats', icon: '🌾', amount: '300 g' },
            { name: 'Milk', icon: '🥛', amount: '40 g' },
            { name: 'Honey', icon: '🍯', amount: '10 g' }
        ],
        healthRating: 'safe',
        recommendation: 'Mostly Safe'
    }
};

// Image Upload Handler
function handleImageUpload(file) {
    return new Promise((resolve, reject) => {
        if (!file) {
            reject('No file selected');
            return;
        }
        
        if (!file.type.startsWith('image/')) {
            reject('Please upload an image file');
            return;
        }
        
        const reader = new FileReader();
        reader.onload = (e) => {
            AppState.uploadedImage = e.target.result;
            resolve(e.target.result);
        };
        reader.onerror = (e) => reject('Error reading file');
        reader.readAsDataURL(file);
    });
}

// Analyze food using Backend API
async function analyzeFood(file) {
    try {
        showToast('Analyzing your food...', 'info');
        
        // Create FormData and append the image file
        const formData = new FormData();
        formData.append('image', file);
        
        const apiUrl = `${API_CONFIG.baseURL}${API_CONFIG.endpoints.analyze}`;
        console.log('Making request to:', apiUrl);
        
        // Call the backend API
        const response = await fetch(apiUrl, {
            method: 'POST',
            body: formData
        });
        
        console.log('Response status:', response.status);
        console.log('Response ok:', response.ok);
        console.log('Response headers:', Object.fromEntries(response.headers.entries()));
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        
        console.log('Backend response:', result); // Debug backend response
        console.log('result.data type:', typeof result.data);
        console.log('result.data length:', result.data ? result.data.length : 'N/A');
        console.log('result.data preview:', result.data ? result.data.substring(0, 200) : 'N/A');
        console.log('result.data type:', typeof result.data);
        console.log('result.data length:', result.data ? result.data.length : 'N/A');
        console.log('result.data preview:', result.data ? result.data.substring(0, 200) : 'N/A');
        
        if (result.success && result.data) {
            const foodData = formatFoodData(result.data);
            console.log('Formatted food data:', foodData); // Debug formatted data
            console.log('Food data keys:', Object.keys(foodData));
            console.log('Food data name:', foodData.name);
            console.log('Food data description:', foodData.description);
            AppState.setCurrentFood(foodData);
            AppState.addToHistory(foodData);
            
            showToast('Analysis complete!', 'success');
            return foodData;
        } else {
            console.error('Backend returned success=false or no data');
            console.error('result.success:', result.success);
            console.error('result.data:', result.data);
            console.error('result.message:', result.message);
            throw new Error(result.message || 'Analysis failed');
        }
        
    } catch (error) {
        console.error('Analysis error:', error);
        showToast('Analysis failed: ' + error.message, 'error');
        throw error;
    }
}

// Format backend response data to match frontend structure
function formatFoodData(data) {
    console.log('formatFoodData called with:', typeof data, data); // Debug input
    console.log('Data length:', data ? data.length : 'N/A');
    console.log('Data starts with ```:', data ? data.startsWith('```') : 'N/A');
    console.log('Data includes productName:', data ? data.includes('productName') : 'N/A');
    
    // Handle raw text response from backend
    if (typeof data === 'string') {
        console.log('Data is string, calling parseRawFoodAnalysis');
        return parseRawFoodAnalysis(data);
    }

    // Handle structured response (fallback)
    console.log('Data is object, using structured format');
    return {
        name: data.name || 'Unknown Product',
        emoji: getFoodEmoji(data.name),
        weight: data.weight || 'N/A',
        nutrition: {
            carbs: data.nutrition?.carbs || 0,
            fats: data.nutrition?.fats || 0,
            sugar: data.nutrition?.sugar || 0,
            calories: data.nutrition?.calories || 0,
            protein: data.nutrition?.protein || 0
        },
        ingredients: formatIngredients(data.ingredients || []),
        healthRating: data.healthRating || 'unknown',
        recommendation: data.recommendation || 'Consult nutritionist',
        additionalNotes: data.additionalNotes || '',
        rawResponse: data.rawResponse || data,
        description: data.description || ''
    };
}

// Parse raw text analysis from LLM
function parseRawFoodAnalysis(rawText) {
    console.log('🔍 Starting JSON parsing...');
    console.log('Raw text length:', rawText.length);
    console.log('Raw text preview:', rawText.substring(0, 200) + '...');
    console.log('Full raw text:', rawText); // Add full text for debugging



    const analysis = {
        name: 'Analyzed Product',
        emoji: '🍽️',
        weight: 'N/A',
        nutrition: { carbs: 0, fats: 0, sugar: 0, calories: 0, protein: 0, fiber: 0, sodium: 0 },
        ingredients: [],
        healthRating: 'unknown',
        recommendation: 'Consult nutritionist',
        additionalNotes: '',
        rawResponse: rawText,
        description: rawText
    };

    // Quick test: try to parse the JSON directly from the backend response
    try {
        const testJson = JSON.parse(rawText);
        console.log('🎉 BACKEND RETURNED PURE JSON! No parsing needed.');
        return mapJsonToAnalysis(testJson);
    } catch (e) {
        console.log('Backend did not return pure JSON, trying extraction methods...');
    }
    let jsonData = null;

        // Method 1: Try markdown code blocks FIRST (most likely for current backend)
        console.log('Trying Method 1 - markdown code blocks');
        // More explicit regex for markdown code blocks
        const markdownRegex = /```\s*json\s*\n(\{[\s\S]*?\})\n```/;
        let jsonMatch = rawText.match(markdownRegex);
        console.log('Method 1 - explicit markdown regex match:', !!jsonMatch);
        
        if (!jsonMatch) {
            // Try more flexible regex
            const flexibleRegex = /```(?:json)?[\s\n]*(\{[\s\S]*?\})[\s\n]*```/;
            jsonMatch = rawText.match(flexibleRegex);
            console.log('Method 1 - flexible markdown regex match:', !!jsonMatch);
        }
        
        if (jsonMatch) {
            console.log('Method 1 - matched text:', jsonMatch[0]);
            console.log('Method 1 - captured JSON:', jsonMatch[1].substring(0, 100));
            try {
                jsonData = JSON.parse(jsonMatch[1]);
                console.log('✅ Successfully parsed JSON from markdown');
            } catch (e) {
                console.log('❌ Markdown JSON parse failed:', e.message);
            }
        }

        // Method 2: Try to parse the entire response as direct JSON
        if (!jsonData) {
            const trimmedText = rawText.trim();
            console.log('Method 2 - trimmedText starts with {:', trimmedText.startsWith('{'));
            console.log('Method 2 - trimmedText ends with }:', trimmedText.endsWith('}'));
            if (trimmedText.startsWith('{') && trimmedText.endsWith('}')) {
                try {
                    jsonData = JSON.parse(trimmedText);
                    console.log('✅ Successfully parsed as direct JSON');
                } catch (e) {
                    console.log('❌ Direct JSON parse failed:', e.message);
                }
            }
        }

        // Method 3: If direct parse failed, try to extract JSON from text
        if (!jsonData) {
            console.log('Trying Method 3 - extract JSON from text');
            // Look for JSON object in the text
            const startBrace = rawText.indexOf('{');
            const endBrace = rawText.lastIndexOf('}');

            console.log('Method 3 - startBrace:', startBrace, 'endBrace:', endBrace);
            if (startBrace !== -1 && endBrace !== -1 && endBrace > startBrace) {
                const jsonCandidate = rawText.substring(startBrace, endBrace + 1);
                console.log('Method 3 - jsonCandidate length:', jsonCandidate.length);
                console.log('Method 3 - jsonCandidate preview:', jsonCandidate.substring(0, 100));
                try {
                    jsonData = JSON.parse(jsonCandidate);
                    console.log('✅ Successfully extracted and parsed JSON');
                } catch (e) {
                    console.log('❌ JSON extraction failed:', e.message);
                }
            }
        }

        // Method 4: Try to find and extract JSON from anywhere in the text
        if (!jsonData) {
            console.log('Trying Method 4 - extract from anywhere');
            // Look for the first { and last } in the entire text
            const firstBrace = rawText.indexOf('{');
            const lastBrace = rawText.lastIndexOf('}');
            
            console.log('Method 4 - firstBrace:', firstBrace, 'lastBrace:', lastBrace);
            if (firstBrace !== -1 && lastBrace !== -1 && lastBrace > firstBrace) {
                const potentialJson = rawText.substring(firstBrace, lastBrace + 1);
                // Make sure it looks like valid JSON (not too short, not too long)
                console.log('Method 4 - potential JSON length:', potentialJson.length);
                if (potentialJson.length > 10 && potentialJson.length < 10000) {
                    try {
                        jsonData = JSON.parse(potentialJson);
                        console.log('✅ Successfully extracted JSON from text');
                    } catch (e) {
                        console.log('❌ JSON extraction from text failed:', e.message);
                    }
                } else {
                    console.log('Method 4 - JSON length out of range');
                }
            }
        }
            console.log('📋 Mapping JSON data to analysis format');
            console.log('JSON keys:', Object.keys(jsonData));

            // Map basic fields
            analysis.name = jsonData.productName || jsonData.name || 'Unknown Product';
            analysis.emoji = getFoodEmoji(analysis.name);
            analysis.weight = jsonData.weight || 'N/A';
            analysis.healthRating = jsonData.healthRating || 'unknown';
            analysis.recommendation = jsonData.recommendation || 'Consult nutritionist';
            analysis.additionalNotes = jsonData.additionalNotes || '';

            // Map nutrition data
            if (jsonData.nutrition) {
                analysis.nutrition = {
                    carbs: jsonData.nutrition.carbs || 0,
                    fats: jsonData.nutrition.fats || 0,
                    sugar: jsonData.nutrition.sugar || 0,
                    calories: jsonData.nutrition.calories || 0,
                    protein: jsonData.nutrition.protein || 0,
                    fiber: jsonData.nutrition.fiber || 0,
                    sodium: jsonData.nutrition.sodium || 0
                };
            }

            // Map ingredients
            if (jsonData.ingredients && Array.isArray(jsonData.ingredients)) {
                analysis.ingredients = jsonData.ingredients.map(ing => ({
                    name: typeof ing === 'string' ? ing : (ing.name || 'Unknown'),
                    icon: getIngredientIcon(typeof ing === 'string' ? ing : (ing.name || 'Unknown')),
                    amount: typeof ing === 'string' ? 'N/A' : (ing.amount || 'N/A')
                }));
            }

            // Create health-oriented description
            analysis.description = createHealthOrientedDescription(jsonData);

            console.log('✅ Successfully parsed and mapped JSON. Product:', analysis.name);
            console.log('Description:', analysis.description.substring(0, 100) + '...');
            console.log('Full parsed analysis:', analysis); // Add full analysis object
        return analysis;


}

// Helper function to map parsed JSON to analysis format
function mapJsonToAnalysis(jsonData) {
    console.log('📋 Mapping pure JSON data to analysis format');
    console.log('JSON keys:', Object.keys(jsonData));

    const analysis = {
        name: 'Analyzed Product',
        emoji: '🍽️',
        weight: 'N/A',
        nutrition: { carbs: 0, fats: 0, sugar: 0, calories: 0, protein: 0, fiber: 0, sodium: 0 },
        ingredients: [],
        healthRating: 'unknown',
        recommendation: 'Consult nutritionist',
        additionalNotes: '',
        rawResponse: JSON.stringify(jsonData),
        description: ''
    };

    // Map basic fields
    analysis.name = jsonData.productName || jsonData.name || 'Unknown Product';
    analysis.emoji = getFoodEmoji(analysis.name);
    analysis.weight = jsonData.weight || 'N/A';
    analysis.healthRating = jsonData.healthRating || 'unknown';
    analysis.recommendation = jsonData.recommendation || 'Consult nutritionist';
    analysis.additionalNotes = jsonData.additionalNotes || '';

    // Map nutrition data
    if (jsonData.nutrition) {
        analysis.nutrition = {
            carbs: jsonData.nutrition.carbs || 0,
            fats: jsonData.nutrition.fats || 0,
            sugar: jsonData.nutrition.sugar || 0,
            calories: jsonData.nutrition.calories || 0,
            protein: jsonData.nutrition.protein || 0,
            fiber: jsonData.nutrition.fiber || 0,
            sodium: jsonData.nutrition.sodium || 0
        };
    }

    // Map ingredients
    if (jsonData.ingredients && Array.isArray(jsonData.ingredients)) {
        analysis.ingredients = jsonData.ingredients.map(ing => ({
            name: typeof ing === 'string' ? ing : (ing.name || 'Unknown'),
            icon: getIngredientIcon(typeof ing === 'string' ? ing : (ing.name || 'Unknown')),
            amount: typeof ing === 'string' ? 'N/A' : (ing.amount || 'N/A')
        }));
    }

    // Create health-oriented description
    analysis.description = createHealthOrientedDescription(jsonData);

    console.log('✅ Successfully mapped pure JSON. Product:', analysis.name);
    return analysis;
}

// Create a human-readable description from parsed data
function createHumanReadableDescription(analysis, rawText) {
    // If we have JSON data, use the health-oriented description
    if (analysis.rawResponse && analysis.rawResponse.includes('{')) {
        try {
            const jsonMatch = analysis.rawResponse.match(/```json\s*\n?(\{[\s\S]*?\})\s*\n?```/) ||
                             analysis.rawResponse.match(/\{[\s\S]*\}/);
            if (jsonMatch) {
                const jsonText = jsonMatch[1] || jsonMatch[0];
                const jsonData = JSON.parse(jsonText);
                return createHealthOrientedDescription(jsonData);
            }
        } catch (e) {
            console.warn('Failed to parse JSON for description:', e);
        }
    }

    // Fallback to original logic
    let description = '';

    // Start with a brief product description
    if (analysis.name && analysis.name !== 'Analyzed Product') {
        description += `${analysis.name} is a `;
    } else {
        description += 'This is a ';
    }

    // Add basic nutritional summary
    const nutrition = analysis.nutrition;
    if (nutrition.calories > 0) {
        description += `${nutrition.calories} calorie `;
    }

    // Add main nutrients
    const nutrients = [];
    if (nutrition.protein > 0) nutrients.push(`${nutrition.protein}g protein`);
    if (nutrition.carbs > 0) nutrients.push(`${nutrition.carbs}g carbs`);
    if (nutrition.fats > 0) nutrients.push(`${nutrition.fats}g fat`);

    if (nutrients.length > 0) {
        description += `food containing ${nutrients.join(', ')}. `;
    } else {
        description += 'food product. ';
    }

    // Add health recommendation
    if (analysis.recommendation && analysis.recommendation !== 'Consult nutritionist') {
        description += analysis.recommendation.toLowerCase();
        if (!description.endsWith('.')) description += '.';
        description += ' ';
    }

    // Add serving size if available
    if (analysis.weight && analysis.weight !== 'N/A') {
        description += `Typical serving size is ${analysis.weight}. `;
    }

    // Add key ingredients if available
    if (analysis.ingredients && analysis.ingredients.length > 0) {
        const mainIngredients = analysis.ingredients.slice(0, 3).map(ing => ing.name).join(', ');
        description += `Main ingredients include ${mainIngredients}.`;
    }

    // If description is too short, add a fallback
    if (description.length < 50) {
        description = 'This food product has been analyzed for nutritional content and safety. Please check the detailed breakdown below for complete information.';
    }

    return description;
}

// Create health-oriented description
function createHealthOrientedDescription(jsonData) {
    let description = '';

    // Start with a critical analysis introduction
    description += `Health analysis of ${jsonData.productName || 'this product'}: `;

    // Add critical nutritional analysis
    if (jsonData.nutrition) {
        const nutrition = jsonData.nutrition;
        const calories = nutrition.calories || 0;
        const sugar = nutrition.sugar || 0;
        const protein = nutrition.protein || 0;
        const fats = nutrition.fats || 0;
        const carbs = nutrition.carbs || 0;

        // Critical calorie analysis
        if (calories > 300) {
            description += `High calorie content (${calories} kcal) makes this unsuitable for weight management. `;
        } else if (calories > 150) {
            description += `Moderate calorie content (${calories} kcal) - acceptable in small portions. `;
        } else if (calories > 0) {
            description += `Low calorie (${calories} kcal) but check nutritional balance. `;
        }

        // Critical sugar analysis
        if (sugar > 15) {
            description += `Extremely high sugar content (${sugar}g) poses serious health risks including diabetes and obesity. `;
        } else if (sugar > 10) {
            description += `High sugar content (${sugar}g) - limit consumption to avoid metabolic issues. `;
        } else if (sugar > 5) {
            description += `Moderate sugar (${sugar}g) - monitor intake for dental health. `;
        }

        // Critical fat analysis
        if (fats > 20) {
            description += `High fat content (${fats}g) increases cardiovascular risk. `;
        } else if (fats > 10) {
            description += `Moderate fat content (${fats}g) - check for saturated fats. `;
        }

        // Protein assessment
        if (protein < 2) {
            description += `Very low protein content - not nutritionally complete. `;
        } else if (protein > 10) {
            description += `Good protein source (${protein}g) for muscle maintenance. `;
        }
    }

    // Critical health rating analysis
    if (jsonData.healthRating) {
        switch (jsonData.healthRating.toLowerCase()) {
            case 'safe':
                description += `Rated as generally safe, but individual health conditions may vary. `;
                break;
            case 'occasional':
                description += `Should be consumed occasionally due to nutritional concerns. `;
                break;
            case 'high-risk':
                description += `High-risk product - significant health concerns require careful consideration. `;
                break;
        }
    }

    // Critical ingredient analysis
    if (jsonData.ingredients && jsonData.ingredients.length > 0) {
        const ingredients = jsonData.ingredients;
        const concerningIngredients = [];

        // Check for common concerning ingredients
        ingredients.forEach(ing => {
            const name = (typeof ing === 'string' ? ing : ing.name || '').toLowerCase();
            if (name.includes('sugar') || name.includes('syrup') || name.includes('fructose')) {
                concerningIngredients.push('added sugars');
            }
            if (name.includes('salt') || name.includes('sodium')) {
                concerningIngredients.push('high sodium');
            }
            if (name.includes('artificial') || name.includes('preservative')) {
                concerningIngredients.push('artificial additives');
            }
        });

        if (concerningIngredients.length > 0) {
            description += `Contains ${concerningIngredients.join(', ')} which may impact long-term health. `;
        }

        const keyIngredients = ingredients.slice(0, 3).map(ing =>
            typeof ing === 'string' ? ing : (ing.name || 'Unknown')
        );
        description += `Primary ingredients: ${keyIngredients.join(', ')}. `;
    }

    // Add critical recommendation
    if (jsonData.recommendation) {
        description += `Recommendation: ${jsonData.recommendation}. `;
    }

    // Add critical additional notes
    if (jsonData.additionalNotes) {
        description += jsonData.additionalNotes;
    }

    return description;
}

// Get appropriate emoji for food type
function getFoodEmoji(foodName) {
    const name = (foodName || '').toLowerCase();
    const emojiMap = {
        'chicken': '🍗', 'meat': '🍖', 'beef': '🥩', 'pork': '🥓',
        'tomato': '🍅', 'pasta': '🍝', 'pizza': '🍕',
        'bread': '🍞', 'cheese': '🧀', 'milk': '🥛',
        'egg': '🥚', 'fish': '🐟', 'shrimp': '🦐',
        'rice': '🍚', 'noodle': '🍜', 'soup': '🍲',
        'salad': '🥗', 'fruit': '🍎', 'vegetable': '🥬',
        'cookie': '🍪', 'cake': '🍰', 'chocolate': '🍫',
        'drink': '🥤', 'juice': '🧃', 'coffee': '☕'
    };
    
    for (const [key, emoji] of Object.entries(emojiMap)) {
        if (name.includes(key)) return emoji;
    }
    return '🍽️';
}

// Format ingredients array
function formatIngredients(ingredients) {
    if (Array.isArray(ingredients)) {
        return ingredients.map((ing, idx) => {
            if (typeof ing === 'string') {
                // Parse string format "ingredient - amount"
                const parts = ing.split('-').map(p => p.trim());
                return {
                    name: parts[0] || `Ingredient ${idx + 1}`,
                    icon: getIngredientIcon(parts[0]),
                    amount: parts[1] || 'N/A'
                };
            }
            return ing;
        });
    }
    return [];
}

// Get icon for ingredient
function getIngredientIcon(ingredientName) {
    const name = (ingredientName || '').toLowerCase();
    const iconMap = {
        'tomato': '🍅', 'sugar': '🍬', 'garlic': '🧄', 'salt': '🧂',
        'onion': '🧅', 'pepper': '🌶️', 'oil': '🛢️', 'butter': '🧈',
        'flour': '🌾', 'egg': '🥚', 'milk': '🥛', 'cheese': '🧀',
        'chicken': '🍗', 'meat': '🥩', 'fish': '🐟', 'water': '💧',
        'honey': '🍯', 'nut': '🥜', 'oat': '🌾'
    };
    
    for (const [key, icon] of Object.entries(iconMap)) {
        if (name.includes(key)) return icon;
    }
    return '📦';
}

// Toast Notification System
function showToast(message, type = 'info') {
    // Remove existing toast
    const existingToast = document.querySelector('.toast');
    if (existingToast) {
        existingToast.remove();
    }
    
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    const icon = type === 'success' ? '✅' : type === 'error' ? '❌' : 'ℹ️';
    toast.innerHTML = `
        <span style="font-size: 24px;">${icon}</span>
        <span>${message}</span>
    `;
    
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.style.animation = 'fadeOut 0.3s ease-out';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// Format nutrition data for display
function formatNutrition(value) {
    return typeof value === 'number' ? value.toFixed(1) : value;
}

// Generate health badge HTML
function getHealthBadge(rating) {
    const badges = {
        'high-risk': { class: 'badge-high-risk', icon: '☁️', text: 'High Risk' },
        'occasional': { class: 'badge-occasional', icon: '🍊', text: 'Consume Occasionally' },
        'safe': { class: 'badge-safe', icon: '✅', text: 'Mostly Safe' }
    };
    
    const badge = badges[rating] || badges['occasional'];
    return `<div class="health-badge ${badge.class}">${badge.icon} ${badge.text}</div>`;
}

// Search functionality
function searchFood(query) {
    query = query.toLowerCase().trim();
    const results = Object.values(FoodDatabase).filter(food => 
        food.name.toLowerCase().includes(query)
    );
    return results;
}

// Navigation helper
function navigateTo(page) {
    window.location.href = page;
}

// Test function to debug markdown parsing
function testMarkdownParsing() {
    const testText = '```json\n{\n  "productName": "Coca-Cola Classic",\n  "description": "test"\n}\n```';
    console.log('Testing markdown parsing with:', testText);
    
    const regex = /```(?:json)?\s*\n?(\{[\s\S]*?\})\s*\n?```/;
    const match = testText.match(regex);
    console.log('Regex match result:', match);
    
    if (match) {
        try {
            const json = JSON.parse(match[1]);
            console.log('Parsed JSON:', json);
        } catch (e) {
            console.log('JSON parse error:', e);
        }
    }
}

// Call test on page load
document.addEventListener('DOMContentLoaded', function() {
    console.log('Food Analysis App Initialized');
    testMarkdownParsing(); // Test the regex
    
    // Add fade-in animation to main content
    const mainContent = document.querySelector('.main-content');
    if (mainContent) {
        mainContent.classList.add('fade-in');
    }
});

// Export functions for use in other files
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        AppState,
        FoodDatabase,
        handleImageUpload,
        analyzeFood,
        showToast,
        formatNutrition,
        getHealthBadge,
        searchFood,
        navigateTo
    };
}