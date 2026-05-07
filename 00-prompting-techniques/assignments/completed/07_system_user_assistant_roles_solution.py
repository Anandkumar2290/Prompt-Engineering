"""
Assignment 07 — System/User/Assistant Roles Solution
Task: Create a customer service chatbot with defined roles
"""

import sys
from pathlib import Path

# allow importing from project root
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from helper import get_completion

system_prompt = """You are a helpful customer service representative for an e-commerce company called TechStore. 
Your role is to:
- Be polite and professional
- Provide accurate information about products and orders
- Handle complaints with empathy
- Offer solutions when possible
- Escalate complex issues to senior staff

You should always maintain a friendly but professional tone."""

user_prompt = """Hi, I ordered a laptop last week but it hasn't arrived yet. The tracking number says it was delivered yesterday, but I never received it. What should I do?"""

full_prompt = f"""System: {system_prompt}

User: {user_prompt}

Assistant:"""

response = get_completion(full_prompt)

print("System Prompt:")
print("-" * 50)
print(system_prompt)

print("\nUser Prompt:")
print("-" * 50)
print(user_prompt)

print("\nResponse:")
print("-" * 50)
print(response)
