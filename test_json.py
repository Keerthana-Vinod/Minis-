import json
import re

test_response = '''```json
{
  "productName": "Coca-Cola Classic",
  "description": "This sugary soft drink contains high fructose corn syrup that contributes to obesity, diabetes, and dental decay. The phosphoric acid can affect bone health, and caffeine may cause dependency.",
  "weight": "355ml",
  "nutrition": {
    "calories": 140,
    "carbs": 39,
    "protein": 0,
    "fats": 0,
    "sugar": 39
  },
  "ingredients": ["carbonated water", "high fructose corn syrup", "caramel color", "phosphoric acid", "natural flavors", "caffeine"],
  "healthRating": "high_risk",
  "recommendation": "Avoid regular consumption due to high sugar and health risks",
  "additionalNotes": "Contributes to obesity, diabetes, and dental problems"
}
```'''

print('Testing JSON parsing from markdown...')
try:
    json_pattern = r'```(?:json)?\s*\n(.*?)\n```'
    match = re.search(json_pattern, test_response, re.DOTALL)
    if match:
        json_str = match.group(1).strip()
        data = json.loads(json_str)
        print('✅ JSON parsed successfully!')
        print(f'Product: {data["productName"]}')
        print(f'Description: {data["description"][:100]}...')
    else:
        print('❌ No JSON found in markdown')
except Exception as e:
    print(f'❌ Parse error: {e}')