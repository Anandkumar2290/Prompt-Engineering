"""
Assignment 13_02 — Scope Guardrails Solution
Task: Create a workflow that enforces scope boundaries
"""

import sys
from pathlib import Path

# allow importing from project root
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from helper import get_completion

class ScopeGuardrails:
    """
    Enforce scope boundaries for different AI assistant roles
    """
    
    def __init__(self):
        self.scope_definitions = {
            "customer_service": {
                "allowed_topics": ["product_info", "order_status", "returns", "billing", "technical_support"],
                "blocked_topics": ["legal_advice", "medical_advice", "financial_planning", "company_secrets"],
                "response_limits": {
                    "max_length": 300,
                    "can_make_promises": False,
                    "can_discuss_competitors": False,
                    "can_provide_pricing": True
                }
            },
            "medical_assistant": {
                "allowed_topics": ["general_health_info", "symptom_explanation", "wellness_tips", "prevention"],
                "blocked_topics": ["diagnosis", "prescription", "specific_treatment", "prognosis"],
                "response_limits": {
                    "max_length": 400,
                    "can_make_promises": False,
                    "must_include_disclaimer": True,
                    "can_suggest_doctor_visit": True
                }
            },
            "financial_advisor": {
                "allowed_topics": ["general_financial_info", "investment_concepts", "budgeting_tips", "retirement_planning"],
                "blocked_topics": ["specific_stock_recommendations", "guaranteed_returns", "tax_advice", "insider_info"],
                "response_limits": {
                    "max_length": 350,
                    "must_include_disclaimer": True,
                    "can_discuss_risk": True,
                    "cannot_predict_market": True
                }
            }
        }
    
    def check_scope_violations(self, user_query, assistant_role):
        """
        Check if user query violates scope boundaries
        """
        scope = self.scope_definitions.get(assistant_role, {})
        
        violations = []
        warnings = []
        
        query_lower = user_query.lower()
        
        # Check for blocked topics
        blocked_topics = scope.get("blocked_topics", [])
        for topic in blocked_topics:
            if topic.replace("_", " ") in query_lower:
                violations.append(f"❌ Blocked topic detected: {topic.replace('_', ' ')}")
        
        # Check if query is within allowed topics
        allowed_topics = scope.get("allowed_topics", [])
        topic_found = False
        for topic in allowed_topics:
            if topic.replace("_", " ") in query_lower:
                topic_found = True
                break
        
        if not topic_found and allowed_topics:
            warnings.append(f"⚠️ Query may be outside scope. Allowed topics: {', '.join(allowed_topics)}")
        
        # Check for problematic patterns
        problematic_patterns = {
            "customer_service": ["lawsuit", "sue", "legal action", "compensation claim"],
            "medical_assistant": ["diagnose me", "what do i have", "prescribe", "cure"],
            "financial_advisor": ["guarantee", "sure thing", "risk-free", "insider"]
        }
        
        patterns = problematic_patterns.get(assistant_role, [])
        for pattern in patterns:
            if pattern in query_lower:
                violations.append(f"❌ Problematic pattern detected: '{pattern}'")
        
        return violations, warnings
    
    def create_scope_limited_prompt(self, user_query, assistant_role):
        """
        Create a prompt that enforces scope boundaries
        """
        scope = self.scope_definitions.get(assistant_role, {})
        limits = scope.get("response_limits", {})
        
        base_prompt = f"""
You are a {assistant_role.replace('_', ' ').title()} AI assistant.

SCOPE GUIDELINES:
- Only discuss topics within your expertise
- Do not provide information outside your scope
- Be helpful but stay within boundaries
"""
        
        # Add role-specific guidelines
        if assistant_role == "customer_service":
            base_prompt += """
CUSTOMER SERVICE RULES:
- Help with product information, orders, returns, billing, and basic technical support
- Do not provide legal advice, medical advice, or financial planning
- Do not make promises about future outcomes
- Do not discuss company competitors or internal matters
- Keep responses under 300 words
"""
        elif assistant_role == "medical_assistant":
            base_prompt += """
MEDICAL ASSISTANT RULES:
- Provide general health information and wellness tips
- NEVER diagnose conditions or prescribe treatments
- Always include disclaimer: "I am not a medical professional"
- Suggest consulting healthcare providers for specific concerns
- Do not make promises about health outcomes
"""
        elif assistant_role == "financial_advisor":
            base_prompt += """
FINANCIAL ADVISOR RULES:
- Provide general financial education and concepts
- NEVER recommend specific stocks or guarantee returns
- Always include disclaimer: "This is not financial advice"
- Discuss investment risks honestly
- Do not predict market movements
"""
        
        base_prompt += f"""

User Query: {user_query}

Response:"""
        
        return base_prompt

# Test cases
test_cases = [
    {
        "name": "Customer Service - In Scope",
        "query": "What is your return policy for electronics?",
        "role": "customer_service",
        "expected": "valid"
    },
    {
        "name": "Customer Service - Out of Scope",
        "query": "Can you help me file a lawsuit against your company?",
        "role": "customer_service", 
        "expected": "violation"
    },
    {
        "name": "Medical Assistant - In Scope",
        "query": "What are some general tips for maintaining good heart health?",
        "role": "medical_assistant",
        "expected": "valid"
    },
    {
        "name": "Medical Assistant - Out of Scope",
        "query": "Can you diagnose my headache and prescribe medication?",
        "role": "medical_assistant",
        "expected": "violation"
    },
    {
        "name": "Financial Advisor - In Scope",
        "query": "Can you explain the concept of diversification in investing?",
        "role": "financial_advisor",
        "expected": "valid"
    },
    {
        "name": "Financial Advisor - Out of Scope",
        "query": "Should I buy Apple stock right now? Will it guarantee good returns?",
        "role": "financial_advisor",
        "expected": "violation"
    }
]

# Run scope guardrails demo
guardrails = ScopeGuardrails()

print("=== Scope Guardrails Demo ===\n")

for test_case in test_cases:
    print(f"🧪 Test: {test_case['name']}")
    print(f"📝 Query: {test_case['query']}")
    print(f"👤 Role: {test_case['role']}")
    
    violations, warnings = guardrails.check_scope_violations(test_case['query'], test_case['role'])
    
    print("\n📊 Scope Check Results:")
    for violation in violations:
        print(f"   {violation}")
    for warning in warnings:
        print(f"   {warning}")
    
    if not violations:
        print("   ✅ Query is within scope")
        print("\n🤖 Model Response:")
        prompt = guardrails.create_scope_limited_prompt(test_case['query'], test_case['role'])
        try:
            response = get_completion(prompt)
            print(response[:350] + "..." if len(response) > 350 else response)
        except Exception as e:
            print(f"Error calling model: {e}")
    else:
        print("   ❌ Query violates scope boundaries - Model not called")
    
    print("\n" + "="*60 + "\n")
