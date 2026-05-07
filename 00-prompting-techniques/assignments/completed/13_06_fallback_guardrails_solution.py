"""
Assignment 13_06 — Fallback Guardrails Solution
Task: Create a workflow with fallback mechanisms when primary responses fail
"""

import sys
from pathlib import Path
import time
import random

# allow importing from project root
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from helper import get_completion

class FallbackGuardrails:
    """
    Implement fallback mechanisms for robust AI responses
    """
    
    def __init__(self):
        self.fallback_strategies = {
            "retry_with_different_prompt": {
                "description": "Rephrase the prompt and try again",
                "max_attempts": 3,
                "prompt_variations": [
                    "simple", "detailed", "step_by_step", "example_based"
                ]
            },
            "simplified_request": {
                "description": "Break down complex request into simpler parts",
                "complexity_threshold": 100,  # characters
                "simplification_factor": 0.5
            },
            "template_response": {
                "description": "Use predefined template when generation fails",
                "templates": {
                    "general_help": "I'm here to help. Could you please rephrase your question or provide more details?",
                    "technical_issue": "I'm experiencing technical difficulties. Please try again in a moment.",
                    "unclear_request": "I'm not sure I understand. Could you clarify what you're looking for?",
                    "scope_limitation": "That's outside my current capabilities. Let me help with something else."
                }
            },
            "graceful_degradation": {
                "description": "Provide partial response with explanation",
                "min_response_length": 50,
                "fallback_prefix": "I can provide some basic information:"
            },
            "escalation": {
                "description": "Escalate to human or higher-level system",
                "escalation_triggers": ["legal_advice", "medical_diagnosis", "financial_planning"],
                "escalation_message": "This requires specialized expertise. Let me connect you with appropriate resources."
            }
        }
        
        self.response_quality_indicators = {
            "too_short": 20,  # characters
            "too_long": 2000,  # characters
            "repetition_threshold": 0.3,  # 30% repeated content
            "error_keywords": ["error", "unable", "cannot", "failed", "sorry"]
        }
    
    def assess_response_quality(self, response):
        """
        Assess the quality of AI response
        """
        quality_score = {
            "is_acceptable": True,
            "issues": [],
            "score": 100,
            "recommendations": []
        }
        
        # Check length
        if len(response) < self.response_quality_indicators["too_short"]:
            quality_score["is_acceptable"] = False
            quality_score["issues"].append("Response too short")
            quality_score["score"] -= 30
        
        if len(response) > self.response_quality_indicators["too_long"]:
            quality_score["issues"].append("Response too long")
            quality_score["score"] -= 10
        
        # Check for error indicators
        response_lower = response.lower()
        for keyword in self.response_quality_indicators["error_keywords"]:
            if keyword in response_lower:
                quality_score["is_acceptable"] = False
                quality_score["issues"].append(f"Contains error indicator: '{keyword}'")
                quality_score["score"] -= 40
        
        # Check for repetition
        words = response.split()
        if len(words) > 10:
            unique_words = set(words)
            repetition_ratio = 1 - (len(unique_words) / len(words))
            if repetition_ratio > self.response_quality_indicators["repetition_threshold"]:
                quality_score["issues"].append("High repetition detected")
                quality_score["score"] -= 20
        
        # Check for empty or meaningless responses
        if not response.strip() or response.strip() in ["I don't know", "I cannot help", ""]:
            quality_score["is_acceptable"] = False
            quality_score["issues"].append("Empty or unhelpful response")
            quality_score["score"] -= 50
        
        # Generate recommendations
        if quality_score["score"] < 70:
            quality_score["recommendations"].append("Consider retry with different prompt")
        if quality_score["score"] < 50:
            quality_score["recommendations"].append("Use fallback template response")
        if quality_score["score"] < 30:
            quality_score["recommendations"].append("Escalate to human support")
        
        return quality_score
    
    def create_fallback_prompt(self, original_query, strategy, attempt=1):
        """
        Create fallback prompt based on strategy
        """
        if strategy == "simple":
            return f"Please answer this question simply: {original_query}"
        
        elif strategy == "detailed":
            return f"""Please provide a detailed and comprehensive answer to this question:
            
Question: {original_query}

Please include:
1. Direct answer
2. Supporting details
3. Examples if relevant
4. Any important considerations"""
        
        elif strategy == "step_by_step":
            return f"""Please answer this question step by step:

Question: {original_query}

Break down your response into clear, logical steps."""
        
        elif strategy == "example_based":
            return f"""Please answer this question and provide an example:

Question: {original_query}

Include a practical example to illustrate your answer."""
        
        else:
            return original_query
    
    def get_template_response(self, template_type):
        """
        Get predefined template response
        """
        templates = self.fallback_strategies["template_response"]["templates"]
        return templates.get(template_type, templates["general_help"])
    
    def execute_with_fallbacks(self, user_query, max_total_attempts=3):
        """
        Execute query with multiple fallback strategies
        """
        execution_log = {
            "original_query": user_query,
            "attempts": [],
            "final_response": "",
            "strategy_used": "",
            "success": False
        }
        
        # Strategy 1: Direct attempt
        try:
            response = get_completion(user_query)
            quality = self.assess_response_quality(response)
            
            execution_log["attempts"].append({
                "strategy": "direct",
                "response": response,
                "quality_score": quality["score"],
                "issues": quality["issues"]
            })
            
            if quality["is_acceptable"]:
                execution_log["final_response"] = response
                execution_log["strategy_used"] = "direct"
                execution_log["success"] = True
                return execution_log
        
        except Exception as e:
            execution_log["attempts"].append({
                "strategy": "direct",
                "error": str(e),
                "quality_score": 0
            })
        
        # Strategy 2: Retry with different prompts
        prompt_variations = self.fallback_strategies["retry_with_different_prompt"]["prompt_variations"]
        max_attempts = min(len(prompt_variations), max_total_attempts - 1)
        
        for i in range(max_attempts):
            strategy = prompt_variations[i]
            try:
                fallback_prompt = self.create_fallback_prompt(user_query, strategy, i + 1)
                response = get_completion(fallback_prompt)
                quality = self.assess_response_quality(response)
                
                execution_log["attempts"].append({
                    "strategy": f"retry_{strategy}",
                    "response": response,
                    "quality_score": quality["score"],
                    "issues": quality["issues"]
                })
                
                if quality["is_acceptable"]:
                    execution_log["final_response"] = response
                    execution_log["strategy_used"] = f"retry_{strategy}"
                    execution_log["success"] = True
                    return execution_log
            
            except Exception as e:
                execution_log["attempts"].append({
                    "strategy": f"retry_{strategy}",
                    "error": str(e),
                    "quality_score": 0
                })
        
        # Strategy 3: Template response
        template_response = self.get_template_response("general_help")
        execution_log["attempts"].append({
            "strategy": "template_response",
            "response": template_response,
            "quality_score": 60,  # Baseline score for templates
            "issues": []
        })
        
        execution_log["final_response"] = template_response
        execution_log["strategy_used"] = "template_response"
        execution_log["success"] = True  # Template response is always "successful"
        
        return execution_log

# Test cases
test_cases = [
    {
        "name": "Simple Query - Should Work Directly",
        "query": "What is the capital of France?"
    },
    {
        "name": "Complex Query - May Need Fallback",
        "query": "Explain the complete economic impact of blockchain technology on global finance markets including specific examples and future predictions"
    },
    {
        "name": "Potentially Problematic Query",
        "query": "Can you provide me with specific legal advice for my situation?"
    },
    {
        "name": "Very Short Query",
        "query": "Help"
    },
    {
        "name": "Normal Query",
        "query": "Can you explain the benefits of regular exercise?"
    }
]

# Run fallback guardrails demo
fallback_system = FallbackGuardrails()

print("=== Fallback Guardrails Demo ===\n")

for test_case in test_cases:
    print(f"🧪 Test: {test_case['name']}")
    print(f"📝 Query: {test_case['query']}")
    
    # Execute with fallbacks
    result = fallback_system.execute_with_fallbacks(test_case['query'])
    
    print(f"\n📊 Execution Results:")
    print(f"   Strategy Used: {result['strategy_used']}")
    print(f"   Success: {'✅ Yes' if result['success'] else '❌ No'}")
    print(f"   Total Attempts: {len(result['attempts'])}")
    
    print(f"\n📋 Attempt Details:")
    for i, attempt in enumerate(result['attempts'], 1):
        print(f"   Attempt {i}: {attempt['strategy']}")
        if 'quality_score' in attempt:
            print(f"     Quality Score: {attempt['quality_score']}/100")
        if 'issues' in attempt and attempt['issues']:
            print(f"     Issues: {', '.join(attempt['issues'])}")
        if 'error' in attempt:
            print(f"     Error: {attempt['error']}")
    
    print(f"\n🤖 Final Response:")
    final_response = result['final_response']
    print(final_response[:300] + "..." if len(final_response) > 300 else final_response)
    
    print("\n" + "="*60 + "\n")
