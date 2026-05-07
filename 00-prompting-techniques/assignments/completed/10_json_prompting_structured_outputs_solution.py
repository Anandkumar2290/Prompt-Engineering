"""
Assignment 10 — JSON Prompting Structured Outputs Solution
Task: Generate structured JSON output for product analysis
"""

import sys
from pathlib import Path
import json

# allow importing from project root
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from helper import get_completion

prompt = """
Analyze the following product and return a structured JSON response:

Product: "Wireless Bluetooth Headphones - Noise Cancelling, 30-hour battery life, water-resistant, $199"

Please return the analysis in this exact JSON format:
{
    "product_name": "string",
    "category": "string",
    "key_features": ["string", "string", "string"],
    "price": {
        "amount": number,
        "currency": "string"
    },
    "target_audience": "string",
    "competitiveness": {
        "rating": number,
        "reasoning": "string"
    },
    "marketing_suggestions": ["string", "string"]
}

Only return valid JSON, no additional text or explanations.
"""

response = get_completion(prompt)

print("Prompt:")
print("-" * 50)
print(prompt)

print("\nRaw Response:")
print("-" * 50)
print(response)

# Try to parse as JSON
try:
    parsed_response = json.loads(response)
    print("\nParsed JSON:")
    print("-" * 50)
    print(json.dumps(parsed_response, indent=2))
except json.JSONDecodeError as e:
    print(f"\nJSON Parsing Error: {e}")
    print("Raw response was not valid JSON")
