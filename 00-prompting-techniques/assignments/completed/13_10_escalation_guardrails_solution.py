"""
Assignment 13_10 — Escalation Guardrails Solution
Task: Create a workflow that escalates when AI cannot handle requests appropriately
"""

import sys
from pathlib import Path
import re
from datetime import datetime

# allow importing from project root
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from helper import get_completion

class EscalationGuardrails:
    """
    Implement escalation guardrails for when AI cannot handle requests appropriately
    """
    
    def __init__(self):
        self.escalation_triggers = {
            "emergency": [
                "emergency", "life threatening", "911", "ambulance", 
                "suicide", "kill myself", "hurt myself", "immediate danger"
            ],
            "legal_matters": [
                "lawsuit", "legal advice", "sue", "court", "attorney",
                "legal representation", "file charges"
            ],
            "medical_emergency": [
                "severe pain", "chest pain", "difficulty breathing",
                "unconscious", "bleeding heavily", "overdose"
            ],
            "financial_crisis": [
                "bankruptcy", "debt crisis", "foreclosure", "eviction",
                "cannot pay rent", "financial emergency"
            ],
            "technical_security": [
                "security breach", "hack", "data leak", "unauthorized access",
                "cyber attack", "malware", "virus"
            ],
            "complex_expertise": [
                "specialized expertise", "professional consultation",
                "expert opinion", "certified professional"
            ]
        }
        
        self.escalation_protocols = {
            "emergency": {
                "priority": "CRITICAL",
                "response": "🚨 IMMEDIATE ACTION REQUIRED - Call 911 or emergency services now!",
                "contact_methods": ["911", "Emergency Room", "Poison Control: 1-800-222-1222"],
                "ai_response": "BLOCKED"
            },
            "medical_emergency": {
                "priority": "CRITICAL",
                "response": "🏥 SEEK IMMEDIATE MEDICAL ATTENTION - Call 911 or go to nearest emergency room",
                "contact_methods": ["911", "Emergency Room", "Urgent Care"],
                "ai_response": "EMERGENCY_INFO_ONLY"
            },
            "legal_matters": {
                "priority": "HIGH",
                "response": "⚖️ LEGAL MATTER DETECTED - Consult a qualified attorney immediately",
                "contact_methods": ["State Bar Association", "Legal Aid Society", "Local Law School Clinic"],
                "ai_response": "GENERAL_INFO_ONLY"
            },
            "financial_crisis": {
                "priority": "HIGH",
                "response": "💰 FINANCIAL CRISIS - Contact financial advisor or credit counselor",
                "contact_methods": ["National Foundation for Credit Counseling", "Financial Planner", "Bank Advisor"],
                "ai_response": "GENERAL_GUIDANCE"
            },
            "technical_security": {
                "priority": "HIGH",
                "response": "🔒 SECURITY ISSUE - Contact IT security team immediately",
                "contact_methods": ["IT Security Department", "Cybersecurity Hotline", "System Administrator"],
                "ai_response": "BASIC_PRECAUTIONS"
            },
            "complex_expertise": {
                "priority": "MEDIUM",
                "response": "👨‍💼 EXPERTISE REQUIRED - This needs professional consultation",
                "contact_methods": ["Industry Professional", "Certified Consultant", "Subject Matter Expert"],
                "ai_response": "EDUCATIONAL_ONLY"
            }
        }
        
        self.escalation_log = []
    
    def detect_escalation_need(self, user_input, context="general"):
        """
        Detect if escalation is needed based on user input
        """
        input_lower = user_input.lower()
        
        for category, triggers in self.escalation_triggers.items():
            for trigger in triggers:
                if trigger in input_lower:
                    return {
                        "escalation_needed": True,
                        "category": category,
                        "trigger": trigger,
                        "urgency": self.escalation_protocols[category]["priority"]
                    }
        
        return {
            "escalation_needed": False,
            "category": None,
            "trigger": None,
            "urgency": None
        }
    
    def assess_ai_capability(self, user_input, context="general"):
        """
        Assess if AI is capable of handling the request appropriately
        """
        capability_assessment = {
            "can_handle": True,
            "confidence": 100,
            "limitations": [],
            "recommendations": []
        }
        
        # Check for complexity indicators
        complexity_indicators = [
            "very complex", "extremely detailed", "highly specialized",
            "expert level", "advanced", "sophisticated"
        ]
        
        input_lower = user_input.lower()
        for indicator in complexity_indicators:
            if indicator in input_lower:
                capability_assessment["confidence"] -= 20
                capability_assessment["limitations"].append("High complexity detected")
        
        # Check for specificity requirements
        if any(word in input_lower for word in ["specific", "exact", "precise", "detailed"]):
            capability_assessment["confidence"] -= 10
            capability_assessment["limitations"].append("High specificity required")
        
        # Check for personal/sensitive information
        sensitive_patterns = [
            r'\bmy\b.*\bcase\b',
            r'\bmy\b.*\bsituation\b',
            r'\bpersonally\b',
            r'\bfor me\b'
        ]
        
        for pattern in sensitive_patterns:
            if re.search(pattern, input_lower):
                capability_assessment["confidence"] -= 15
                capability_assessment["limitations"].append("Personal situation requires individualized attention")
        
        # Determine if AI can handle
        if capability_assessment["confidence"] < 60:
            capability_assessment["can_handle"] = False
            capability_assessment["recommendations"].append("Escalate to human professional")
        
        return capability_assessment
    
    def execute_escalation_protocol(self, escalation_info, user_input):
        """
        Execute appropriate escalation protocol
        """
        category = escalation_info["category"]
        protocol = self.escalation_protocols[category]
        
        escalation_response = {
            "timestamp": datetime.now().isoformat(),
            "category": category,
            "priority": protocol["priority"],
            "user_input": user_input,
            "trigger": escalation_info["trigger"],
            "response_message": protocol["response"],
            "recommended_contacts": protocol["contact_methods"],
            "ai_action": protocol["ai_response"]
        }
        
        # Log escalation
        self.escalation_log.append(escalation_response)
        
        return escalation_response
    
    def create_escalation_aware_prompt(self, user_input, context="general"):
        """
        Create prompt with escalation awareness
        """
        escalation_check = self.detect_escalation_need(user_input, context)
        
        if escalation_check["escalation_needed"]:
            # Don't call AI for critical escalations
            protocol = self.escalation_protocols[escalation_check["category"]]
            if protocol["ai_response"] == "BLOCKED":
                return None, escalation_check
            
            # Limited AI response for other escalations
            return self._create_limited_prompt(user_input, escalation_check), escalation_check
        
        # Check AI capability
        capability = self.assess_ai_capability(user_input, context)
        
        if not capability["can_handle"]:
            escalation_check.update({
                "escalation_needed": True,
                "category": "complex_expertise",
                "trigger": "capability_limitation",
                "urgency": "MEDIUM"
            })
            return self._create_limited_prompt(user_input, escalation_check), escalation_check
        
        # Normal AI response
        return f"""You are a helpful AI assistant. Please provide a comprehensive and accurate response to this query.

USER QUERY: {user_input}

RESPONSE:""", escalation_check
    
    def _create_limited_prompt(self, user_input, escalation_info):
        """
        Create limited prompt for escalation situations
        """
        category = escalation_info["category"]
        protocol = self.escalation_protocols[category]
        
        if protocol["ai_response"] == "BLOCKED":
            return None
        
        if protocol["ai_response"] == "EMERGENCY_INFO_ONLY":
            return f"""The user is experiencing a medical emergency. Provide only basic safety information and immediate emergency guidance.

EMERGENCY QUERY: {user_input}

CRITICAL: Emphasize calling 911 immediately. Do not provide medical advice or diagnosis.

RESPONSE:"""
        
        if protocol["ai_response"] == "GENERAL_INFO_ONLY":
            return f"""The user has a legal matter. Provide only general legal information and concepts.

LEGAL QUERY: {user_query}

IMPORTANT: Explain that you cannot provide legal advice and suggest consulting an attorney.

RESPONSE:"""
        
        return f"""The user requires professional expertise. Provide only general educational information.

QUERY: {user_input}

IMPORTANT: Emphasize the need for professional consultation.

RESPONSE:"""

# Test cases
test_cases = [
    {
        "name": "Medical Emergency - Critical Escalation",
        "query": "I'm having severe chest pain and can't breathe, what should I do?"
    },
    {
        "name": "Legal Matter - High Priority Escalation",
        "query": "I need to sue my employer for wrongful termination, can you help me file the lawsuit?"
    },
    {
        "name": "Financial Crisis - High Priority Escalation",
        "query": "I'm facing bankruptcy and foreclosure, what should I do to save my home?"
    },
    {
        "name": "Security Issue - High Priority Escalation",
        "query": "I think our system has been hacked and customer data is compromised"
    },
    {
        "name": "Complex Expertise - Medium Priority Escalation",
        "query": "I need highly specialized quantum physics calculations for my research"
    },
    {
        "name": "Normal Query - No Escalation",
        "query": "Can you explain the benefits of regular exercise?"
    },
    {
        "name": "Suicidal Ideation - Critical Escalation",
        "query": "I want to end my life, nobody cares about me"
    }
]

# Run escalation guardrails demo
escalation_system = EscalationGuardrails()

print("=== Escalation Guardrails Demo ===\n")

for test_case in test_cases:
    print(f"🧪 Test: {test_case['name']}")
    print(f"📝 Query: {test_case['query']}")
    
    # Detect escalation need
    escalation_info = escalation_system.detect_escalation_need(test_case['query'])
    
    print(f"\n📊 Escalation Analysis:")
    if escalation_info["escalation_needed"]:
        print(f"   🚨 ESCALATION REQUIRED")
        print(f"   Category: {escalation_info['category']}")
        print(f"   Priority: {escalation_info['urgency']}")
        print(f"   Trigger: {escalation_info['trigger']}")
        
        # Execute escalation protocol
        protocol_response = escalation_system.execute_escalation_protocol(escalation_info, test_case['query'])
        
        print(f"\n📋 Escalation Response:")
        print(f"   {protocol_response['response_message']}")
        print(f"   Recommended Contacts: {', '.join(protocol_response['recommended_contacts'])}")
        
        # Check if AI should respond
        if protocol_response['ai_action'] == "BLOCKED":
            print(f"   🤖 AI Response: BLOCKED (Human intervention required)")
        else:
            print(f"   🤖 AI Response: Limited ({protocol_response['ai_action']})")
            
            # Generate limited response
            prompt = escalation_system.create_escalation_aware_prompt(test_case['query'])
            if prompt[0]:
                try:
                    response = get_completion(prompt[0])
                    print(f"   Response: {response[:200]}...")
                except Exception as e:
                    print(f"   Error: {e}")
    
    else:
        print(f"   ✅ No escalation needed")
        
        # Assess AI capability
        capability = escalation_system.assess_ai_capability(test_case['query'])
        print(f"   AI Capability: {'✅ Can handle' if capability['can_handle'] else '⚠️ Limited'}")
        print(f"   Confidence: {capability['confidence']}%")
        
        if capability['limitations']:
            print(f"   Limitations: {', '.join(capability['limitations'])}")
        
        # Generate normal response
        if capability['can_handle']:
            prompt = escalation_system.create_escalation_aware_prompt(test_case['query'])
            try:
                response = get_completion(prompt[0])
                print(f"\n🤖 AI Response:")
                print(response[:300] + "..." if len(response) > 300 else response)
            except Exception as e:
                print(f"   Error: {e}")
    
    print("\n" + "="*60 + "\n")

# Show escalation summary
print(f"\n📊 Escalation Summary:")
print(f"Total Escalations: {len(escalation_system.escalation_log)}")
for log_entry in escalation_system.escalation_log:
    print(f"- {log_entry['category']} ({log_entry['priority']}): {log_entry['trigger']}")
