"""
Assignment 13_09 — Application Guardrails Solution
Task: Create domain-specific guardrails for different applications
"""

import sys
from pathlib import Path
import re
from datetime import datetime

# allow importing from project root
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from helper import get_completion

class ApplicationGuardrails:
    """
    Domain-specific guardrails for different AI applications
    """
    
    def __init__(self):
        self.application_configs = {
            "healthcare_chatbot": {
                "allowed_topics": ["general_health", "wellness", "prevention", "symptoms_info"],
                "blocked_topics": ["diagnosis", "prescription", "specific_treatment", "prognosis"],
                "required_disclaimers": ["medical_disclaimer"],
                "escalation_triggers": ["emergency", "severe_pain", "difficulty_breathing"],
                "response_limits": {
                    "max_length": 300,
                    "can_recommend_doctors": True,
                    "can_suggest_tests": False
                }
            },
            "financial_advisor": {
                "allowed_topics": ["general_finance", "investment_concepts", "budgeting", "retirement_planning"],
                "blocked_topics": ["specific_recommendations", "guaranteed_returns", "market_timing", "insider_info"],
                "required_disclaimers": ["financial_disclaimer"],
                "escalation_triggers": ["debt_crisis", "bankruptcy", "legal_financial_issues"],
                "response_limits": {
                    "max_length": 400,
                    "can_discuss_risk": True,
                    "can_predict_markets": False
                }
            },
            "legal_assistant": {
                "allowed_topics": ["legal_concepts", "procedure_info", "documentation", "general_rights"],
                "blocked_topics": ["specific_legal_advice", "case_outcomes", "strategy", "representation"],
                "required_disclaimers": ["legal_disclaimer"],
                "escalation_triggers": ["lawsuit_filing", "criminal_charges", "immediate_legal_action"],
                "response_limits": {
                    "max_length": 350,
                    "can_explain_laws": True,
                    "can_recommend_lawyers": False
                }
            },
            "educational_tutor": {
                "allowed_topics": ["academic_subjects", "study_methods", "homework_help", "concept_explanation"],
                "blocked_topics": ["exam_answers", "cheating", "plagiarism", "unfair_advantage"],
                "required_disclaimers": ["educational_disclaimer"],
                "escalation_triggers": ["academic_honesty_violations", "grade_disputes"],
                "response_limits": {
                    "max_length": 500,
                    "can_give_hints": True,
                    "can_provide_direct_answers": False
                }
            },
            "customer_service": {
                "allowed_topics": ["product_info", "order_status", "returns", "technical_support", "billing"],
                "blocked_topics": ["company_secrets", "competitor_info", "legal_commitments", "guarantees"],
                "required_disclaimers": ["service_disclaimer"],
                "escalation_triggers": ["legal_threats", "complaint_escalation", "media_inquiry"],
                "response_limits": {
                    "max_length": 300,
                    "can_make_offers": False,
                    "can_discuss_competitors": False
                }
            }
        }
        
        self.disclaimers = {
            "medical_disclaimer": "I am not a medical professional. This information is for educational purposes only. Please consult a healthcare provider for medical advice.",
            "financial_disclaimer": "I am not a financial advisor. This information is educational and should not be considered financial advice. Consult a professional for personalized guidance.",
            "legal_disclaimer": "I am not an attorney. This information is not legal advice. Consult a qualified lawyer for legal matters.",
            "educational_disclaimer": "I provide guidance for learning purposes. Academic integrity is important. Ensure your work follows your institution's guidelines.",
            "service_disclaimer": "I provide general information. For specific account issues or official commitments, please contact our customer service team."
        }
    
    def validate_application_input(self, user_input, application_type):
        """
        Validate input for specific application
        """
        config = self.application_configs.get(application_type, {})
        validation_result = {
            "is_valid": True,
            "violations": [],
            "warnings": [],
            "escalation_needed": False,
            "escalation_reason": ""
        }
        
        input_lower = user_input.lower()
        
        # Check blocked topics
        blocked_topics = config.get("blocked_topics", [])
        for topic in blocked_topics:
            if topic.replace("_", " ") in input_lower:
                validation_result["is_valid"] = False
                validation_result["violations"].append(f"Blocked topic: {topic.replace('_', ' ')}")
        
        # Check escalation triggers
        escalation_triggers = config.get("escalation_triggers", [])
        for trigger in escalation_triggers:
            if trigger.replace("_", " ") in input_lower:
                validation_result["escalation_needed"] = True
                validation_result["escalation_reason"] = f"Escalation trigger: {trigger.replace('_', ' ')}"
        
        # Check if within allowed topics
        allowed_topics = config.get("allowed_topics", [])
        if allowed_topics:
            topic_found = False
            for topic in allowed_topics:
                if topic.replace("_", " ") in input_lower:
                    topic_found = True
                    break
            
            if not topic_found:
                validation_result["warnings"].append(f"Query may be outside scope. Allowed: {', '.join(allowed_topics)}")
        
        return validation_result
    
    def create_application_prompt(self, user_input, application_type):
        """
        Create application-specific prompt with guardrails
        """
        config = self.application_configs.get(application_type, {})
        response_limits = config.get("response_limits", {})
        
        # Base application-specific prompt
        application_prompts = {
            "healthcare_chatbot": f"""
You are a healthcare information assistant. Provide general health information only.

HEALTHCARE GUIDELINES:
- Explain symptoms and conditions in general terms
- Suggest when to see a doctor
- Provide wellness and prevention tips
- NEVER diagnose or prescribe
- Include medical disclaimer

RESPONSE LIMITS:
- Max {response_limits.get('max_length', 300)} words
- Can recommend seeing doctors: {response_limits.get('can_recommend_doctors', True)}
- Can suggest medical tests: {response_limits.get('can_suggest_tests', False)}

""",
            "financial_advisor": f"""
You are a financial education assistant. Provide general financial information only.

FINANCIAL GUIDELINES:
- Explain financial concepts and strategies
- Discuss investment types and risks
- Provide budgeting and planning guidance
- NEVER recommend specific investments
- NEVER guarantee returns
- Include financial disclaimer

RESPONSE LIMITS:
- Max {response_limits.get('max_length', 400)} words
- Can discuss risk: {response_limits.get('can_discuss_risk', True)}
- Can predict markets: {response_limits.get('can_predict_markets', False)}

""",
            "legal_assistant": f"""
You are a legal information assistant. Provide general legal information only.

LEGAL GUIDELINES:
- Explain legal concepts and procedures
- Describe rights and responsibilities
- Provide documentation guidance
- NEVER give specific legal advice
- NEVER predict case outcomes
- Include legal disclaimer

RESPONSE LIMITS:
- Max {response_limits.get('max_length', 350)} words
- Can explain laws: {response_limits.get('can_explain_laws', True)}
- Can recommend lawyers: {response_limits.get('can_recommend_lawyers', False)}

""",
            "educational_tutor": f"""
You are an educational tutor. Help with learning and understanding.

EDUCATIONAL GUIDELINES:
- Explain concepts clearly
- Provide study strategies
- Give hints for problem-solving
- NEVER provide direct exam answers
- NEVER facilitate cheating
- Promote academic integrity

RESPONSE LIMITS:
- Max {response_limits.get('max_length', 500)} words
- Can give hints: {response_limits.get('can_give_hints', True)}
- Can provide direct answers: {response_limits.get('can_provide_direct_answers', False)}

""",
            "customer_service": f"""
You are a customer service assistant. Help with product and service inquiries.

SERVICE GUIDELINES:
- Provide accurate product information
- Help with orders and returns
- Assist with basic technical support
- NEVER make legal commitments
- NEVER discuss company secrets
- Be professional and helpful

RESPONSE LIMITS:
- Max {response_limits.get('max_length', 300)} words
- Can make offers: {response_limits.get('can_make_offers', False)}
- Can discuss competitors: {response_limits.get('can_discuss_competitors', False)}

"""
        }
        
        base_prompt = application_prompts.get(application_type, "")
        
        # Add required disclaimers
        required_disclaimers = config.get("required_disclaimers", [])
        disclaimer_text = ""
        for disclaimer in required_disclaimers:
            if disclaimer in self.disclaimers:
                disclaimer_text += f"\n\n{self.disclaimers[disclaimer]}"
        
        full_prompt = f"""{base_prompt}
USER QUERY: {user_input}

{disclaimer_text}

RESPONSE:"""
        
        return full_prompt
    
    def get_escalation_response(self, escalation_reason, application_type):
        """
        Get appropriate escalation response
        """
        escalation_responses = {
            "healthcare_chatbot": "🚨 This appears to require immediate medical attention. Please call emergency services (911) or go to the nearest emergency room.",
            "financial_advisor": "⚠️ This requires professional financial guidance. Please consult a certified financial advisor or credit counselor.",
            "legal_assistant": "⚖️ This requires legal representation. Please consult a qualified attorney immediately.",
            "educational_tutor": "📚 This requires official academic intervention. Please contact your instructor or academic advisor.",
            "customer_service": "📞 This requires escalation to our senior support team. Please call our customer service hotline."
        }
        
        base_response = escalation_responses.get(application_type, "This requires professional assistance.")
        return f"{base_response}\n\nReason: {escalation_reason}"

# Test cases for different applications
test_cases = [
    {
        "name": "Healthcare - Valid Query",
        "query": "What are some general symptoms of the flu?",
        "application": "healthcare_chatbot"
    },
    {
        "name": "Healthcare - Escalation Needed",
        "query": "I have severe chest pain and difficulty breathing",
        "application": "healthcare_chatbot"
    },
    {
        "name": "Healthcare - Blocked Query",
        "query": "Can you diagnose my headache and prescribe medication?",
        "application": "healthcare_chatbot"
    },
    {
        "name": "Financial - Valid Query",
        "query": "Can you explain the concept of diversification in investing?",
        "application": "financial_advisor"
    },
    {
        "name": "Financial - Blocked Query",
        "query": "Should I buy Tesla stock right now? Will it double?",
        "application": "financial_advisor"
    },
    {
        "name": "Legal - Valid Query",
        "query": "What is the process for filing a small claims case?",
        "application": "legal_assistant"
    },
    {
        "name": "Educational - Valid Query",
        "query": "Can you help me understand how photosynthesis works?",
        "application": "educational_tutor"
    },
    {
        "name": "Customer Service - Valid Query",
        "query": "What is your return policy for electronics?",
        "application": "customer_service"
    }
]

# Run application guardrails demo
app_system = ApplicationGuardrails()

print("=== Application Guardrails Demo ===\n")

for test_case in test_cases:
    print(f"🧪 Test: {test_case['name']}")
    print(f"📝 Query: {test_case['query']}")
    print(f"🏢 Application: {test_case['application']}")
    
    # Validate input
    validation = app_system.validate_application_input(test_case['query'], test_case['application'])
    
    print(f"\n📊 Input Validation:")
    if validation["is_valid"]:
        print("   ✅ Input is valid")
    else:
        print("   ❌ Input has violations")
    
    for violation in validation["violations"]:
        print(f"   {violation}")
    
    for warning in validation["warnings"]:
        print(f"   ⚠️ {warning}")
    
    # Handle escalation
    if validation["escalation_needed"]:
        print(f"\n🚨 ESCALATION REQUIRED:")
        escalation_response = app_system.get_escalation_response(
            validation["escalation_reason"], 
            test_case['application']
        )
        print(escalation_response)
        print("\n" + "="*60 + "\n")
        continue
    
    # Generate response if valid
    if validation["is_valid"]:
        print(f"\n🤖 Application Response:")
        prompt = app_system.create_application_prompt(test_case['query'], test_case['application'])
        
        try:
            response = get_completion(prompt)
            print(response[:450] + "..." if len(response) > 450 else response)
        except Exception as e:
            print(f"Error: {e}")
    else:
        print(f"\n❌ Response blocked due to input violations")
    
    print("\n" + "="*60 + "\n")
