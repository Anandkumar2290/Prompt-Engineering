"""
Assignment 13_04 — Behavior Guardrails Solution
Task: Create a workflow that controls AI behavior and responses
"""

import sys
from pathlib import Path

# allow importing from project root
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from helper import get_completion

class BehaviorGuardrails:
    """
    Control AI behavior, tone, and response patterns
    """
    
    def __init__(self):
        self.behavior_profiles = {
            "professional_assistant": {
                "tone": "professional, respectful, formal",
                "response_style": "structured, informative, concise",
                "allowed_behaviors": ["provide_information", "analyze", "recommend", "explain"],
                "blocked_behaviors": ["casual_chat", "personal_opinions", "emotional_responses"],
                "response_length": "medium (200-400 words)",
                "greeting": "Good day. How may I assist you?",
                "closing": "I hope this information is helpful. Please let me know if you need further assistance."
            },
            "friendly_tutor": {
                "tone": "encouraging, patient, supportive",
                "response_style": "educational, step-by-step, interactive",
                "allowed_behaviors": ["teach", "explain", "give_examples", "ask_questions"],
                "blocked_behaviors": ["give_direct_answers", "frustration", "criticism"],
                "response_length": "detailed (300-500 words)",
                "greeting": "Hello! I'm excited to help you learn. What would you like to explore today?",
                "closing": "Great progress! Keep up the excellent work, and feel free to ask more questions anytime."
            },
            "technical_support": {
                "tone": "efficient, clear, solution-focused",
                "response_style": "problem-solving, step-by-step, action-oriented",
                "allowed_behaviors": ["troubleshoot", "provide_solutions", "escalate", "document"],
                "blocked_behaviors": ["casual_conversation", "emotional_responses", "promises"],
                "response_length": "concise (150-300 words)",
                "greeting": "Technical Support. I'm ready to help resolve your issue.",
                "closing": "Please follow these steps and let me know if the issue persists."
            },
            "creative_partner": {
                "tone": "enthusiastic, imaginative, collaborative",
                "response_style": "brainstorming, suggestive, open-ended",
                "allowed_behaviors": ["brainstorm", "suggest", "inspire", "collaborate"],
                "blocked_behaviors": ["criticism", "limitations", "negative_feedback"],
                "response_length": "flexible (100-600 words)",
                "greeting": "Let's create something amazing together! What's on your mind?",
                "closing": "Wonderful ideas! Keep exploring and let me know how I can help further."
            }
        }
        
        # Universal behavior rules
        self.universal_rules = {
            "always": ["be_helpful", "be_respectful", "maintain_boundaries"],
            "never": ["be_rude", "share_personal_info", "make_assumptions", "ignore_safety"]
        }
    
    def validate_behavior_request(self, user_query, requested_behavior):
        """
        Validate if requested behavior is appropriate for the context
        """
        validation_results = {
            "appropriate": True,
            "warnings": [],
            "suggestions": []
        }
        
        # Check if behavior exists
        if requested_behavior not in self.behavior_profiles:
            validation_results["appropriate"] = False
            validation_results["warnings"].append(f"❌ Unknown behavior profile: {requested_behavior}")
            validation_results["suggestions"].append(f"Available profiles: {list(self.behavior_profiles.keys())}")
            return validation_results
        
        profile = self.behavior_profiles[requested_behavior]
        
        # Check for behavior conflicts
        query_lower = user_query.lower()
        
        # Check for requests that conflict with the profile
        if requested_behavior == "professional_assistant":
            conflict_indicators = ["casual", "friendly chat", "personal story", "how are you feeling"]
            for indicator in conflict_indicators:
                if indicator in query_lower:
                    validation_results["warnings"].append(f"⚠️ Query may conflict with {requested_behavior} tone")
        
        elif requested_behavior == "technical_support":
            conflict_indicators = ["creative writing", "personal advice", "emotional support"]
            for indicator in conflict_indicators:
                if indicator in query_lower:
                    validation_results["warnings"].append(f"⚠️ Query outside technical support scope")
        
        return validation_results
    
    def create_behavior_controlled_prompt(self, user_query, behavior_profile):
        """
        Create a prompt with specific behavior controls
        """
        profile = self.behavior_profiles.get(behavior_profile, {})
        
        prompt = f"""
BEHAVIOR PROFILE: {behavior_profile.replace('_', ' ').title()}

TONE GUIDELINES:
- Maintain a {profile.get('tone', 'neutral')} tone
- Be consistent throughout the response

RESPONSE STYLE:
- Use a {profile.get('response_style', 'clear')} approach
- Target length: {profile.get('response_length', 'medium')}

ALLOWED BEHAVIORS:
{chr(10).join(f"- {behavior}" for behavior in profile.get('allowed_behaviors', ['help', 'inform']))}

BLOCKED BEHAVIORS:
{chr(10).join(f"- {behavior}" for behavior in profile.get('blocked_behaviors', []))}

UNIVERSAL RULES:
Always: {', '.join(self.universal_rules['always'])}
Never: {', '.join(self.universal_rules['never'])}

STRUCTURE:
1. {profile.get('greeting', 'Hello.')}
2. Address the user's query
3. {profile.get('closing', 'Thank you.')}

USER QUERY: {user_query}

RESPONSE:"""
        
        return prompt

# Test cases
test_cases = [
    {
        "name": "Professional Assistant - Appropriate",
        "query": "Can you provide a market analysis for Q3 2024?",
        "behavior": "professional_assistant",
        "expected": "appropriate"
    },
    {
        "name": "Professional Assistant - Conflict",
        "query": "Let's have a casual chat about your weekend plans",
        "behavior": "professional_assistant",
        "expected": "warning"
    },
    {
        "name": "Friendly Tutor - Appropriate",
        "query": "Can you help me understand photosynthesis step by step?",
        "behavior": "friendly_tutor",
        "expected": "appropriate"
    },
    {
        "name": "Technical Support - Appropriate",
        "query": "My computer won't start. What should I check first?",
        "behavior": "technical_support",
        "expected": "appropriate"
    },
    {
        "name": "Creative Partner - Appropriate",
        "query": "Help me brainstorm ideas for a fantasy novel",
        "behavior": "creative_partner",
        "expected": "appropriate"
    },
    {
        "name": "Unknown Behavior Profile",
        "query": "Help me with something",
        "behavior": "unknown_profile",
        "expected": "inappropriate"
    }
]

# Run behavior guardrails demo
behavior_system = BehaviorGuardrails()

print("=== Behavior Guardrails Demo ===\n")

for test_case in test_cases:
    print(f"🧪 Test: {test_case['name']}")
    print(f"📝 Query: {test_case['query']}")
    print(f"🎭 Behavior: {test_case['behavior']}")
    
    validation = behavior_system.validate_behavior_request(test_case['query'], test_case['behavior'])
    
    print("\n📊 Behavior Validation:")
    if validation["appropriate"]:
        print("   ✅ Behavior request is appropriate")
    else:
        print("   ❌ Behavior request has issues")
    
    for warning in validation["warnings"]:
        print(f"   {warning}")
    
    for suggestion in validation["suggestions"]:
        print(f"   💡 {suggestion}")
    
    # Generate response if appropriate
    if validation["appropriate"] and test_case['behavior'] in behavior_system.behavior_profiles:
        print("\n🤖 Behavior-Controlled Response:")
        prompt = behavior_system.create_behavior_controlled_prompt(test_case['query'], test_case['behavior'])
        try:
            response = get_completion(prompt)
            print(response[:400] + "..." if len(response) > 400 else response)
        except Exception as e:
            print(f"Error calling model: {e}")
    
    print("\n" + "="*60 + "\n")
