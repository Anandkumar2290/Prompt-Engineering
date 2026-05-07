"""
Assignment 04 — Multi-shot Prompting Solution
Task: Generate email responses for different scenarios using multiple examples
"""

import sys
from pathlib import Path

# allow importing from project root
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from helper import get_completion

prompt = """
Generate professional email responses based on the scenarios and examples provided.

Examples:
Scenario: Customer complaint about late delivery
Response: "Dear Customer, We sincerely apologize for the delay in your delivery. We are investigating this issue and will ensure your package arrives within 24 hours. As a gesture of goodwill, we'd like to offer you a 15% discount on your next purchase."

Scenario: Request for product information
Response: "Thank you for your interest in our products. I'd be happy to provide you with detailed specifications and pricing. Would you prefer a virtual demonstration or would you like me to send you our product catalog?"

Scenario: Meeting scheduling conflict
Response: "Thank you for reaching out about the meeting. Unfortunately, I have a scheduling conflict at the proposed time. Would any of these alternative times work for you: Tuesday 2 PM, Wednesday 10 AM, or Thursday 3 PM?"

Now generate a response for this scenario:
Scenario: Customer wants to return a defective product
Response:
"""

response = get_completion(prompt)

print("Prompt:")
print("-" * 50)
print(prompt)

print("\nResponse:")
print("-" * 50)
print(response)
