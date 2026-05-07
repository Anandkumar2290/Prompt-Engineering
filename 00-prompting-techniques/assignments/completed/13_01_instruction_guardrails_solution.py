"""
Assignment 13_01 — Instruction Guardrails Solution
Task: Create a workflow with instruction guardrails
"""

import sys
from pathlib import Path

# allow importing from project root
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from helper import get_completion

def validate_instruction_guardrails(user_input, task_type):
    """
    Validate user input against instruction guardrails
    """
    guardrails = {
        "medical": {
            "allowed_keywords": ["symptoms", "diagnosis", "treatment", "medication", "therapy"],
            "blocked_keywords": ["prescribe", "diagnose", "cure", "guarantee"],
            "max_length": 500,
            "required_fields": ["symptoms", "duration"]
        },
        "financial": {
            "allowed_keywords": ["advice", "strategy", "planning", "investment"],
            "blocked_keywords": ["guarantee", "risk-free", "certain profit", "insider"],
            "max_length": 300,
            "required_fields": ["goal", "timeline"]
        },
        "legal": {
            "allowed_keywords": ["information", "guidance", "process", "procedure"],
            "blocked_keywords": ["legal advice", "guarantee outcome", "win case"],
            "max_length": 400,
            "required_fields": ["situation", "jurisdiction"]
        }
    }
    
    rules = guardrails.get(task_type, {})
    
    # Check length
    if len(user_input) > rules.get("max_length", 1000):
        return False, f"Input exceeds maximum length of {rules.get('max_length', 1000)} characters"
    
    # Check for blocked keywords
    blocked = rules.get("blocked_keywords", [])
    for keyword in blocked:
        if keyword.lower() in user_input.lower():
            return False, f"Input contains blocked keyword: '{keyword}'"
    
    # Check for required fields
    required = rules.get("required_fields", [])
    for field in required:
        if field.lower() not in user_input.lower():
            return False, f"Input must mention: '{field}'"
    
    return True, "Input validation passed"

def create_guarded_prompt(user_input, task_type):
    """
    Create a prompt with instruction guardrails
    """
    system_prompt = f"""
You are a helpful AI assistant providing {task_type} information.

IMPORTANT GUIDELINES:
1. Provide general information only, not specific advice
2. Include disclaimer that you're not a professional {task_type} advisor
3. Encourage consultation with qualified professionals
4. Do not make guarantees or promises
5. Stay within your scope of knowledge
6. If unsure, say so and suggest professional help

User Query: {user_input}

Response:
"""
    
    return system_prompt

# Test cases
test_cases = [
    {
        "name": "Valid Medical Query",
        "input": "I have been experiencing headaches and fatigue for the past week. What could be the symptoms?",
        "task_type": "medical",
        "expected": "valid"
    },
    {
        "name": "Blocked Medical Query", 
        "input": "Can you prescribe me medication for my headache?",
        "task_type": "medical",
        "expected": "blocked"
    },
    {
        "name": "Valid Financial Query",
        "input": "I need investment advice for retirement planning with a 20-year timeline",
        "task_type": "financial", 
        "expected": "valid"
    },
    {
        "name": "Invalid Financial Query",
        "input": "Tell me how to get guaranteed profits",
        "task_type": "financial",
        "expected": "blocked"
    }
]

print("=== Instruction Guardrails Demo ===\n")

for test_case in test_cases:
    print(f"Test: {test_case['name']}")
    print(f"Input: {test_case['input']}")
    print(f"Task Type: {test_case['task_type']}")
    
    is_valid, message = validate_instruction_guardrails(test_case['input'], test_case['task_type'])
    
    print(f"Validation Result: {'✅ PASSED' if is_valid else '❌ FAILED'}")
    print(f"Message: {message}")
    
    if is_valid:
        print("\n--- Model Response ---")
        prompt = create_guarded_prompt(test_case['input'], test_case['task_type'])
        response = get_completion(prompt)
        print(response[:300] + "..." if len(response) > 300 else response)
    
    print("-" * 50)
    print()
