"""
Assignment 13_11 — Privacy Guardrails Solution
Task: Create a workflow that protects user privacy and prevents data collection
"""

import sys
from pathlib import Path
import re
import hashlib
from datetime import datetime

# allow importing from project root
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from helper import get_completion

class PrivacyGuardrails:
    """
    Protect user privacy and prevent unauthorized data collection
    """
    
    def __init__(self):
        self.pii_patterns = {
            "phone_number": [
                r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
                r'\b\+?1[-.]?\d{3}[-.]?\d{3}[-.]?\d{4}\b'
            ],
            "email": [
                r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            ],
            "ssn": [
                r'\b\d{3}-\d{2}-\d{4}\b',
                r'\b\d{3}\s\d{2}\s\d{4}\b'
            ],
            "credit_card": [
                r'\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b',
                r'\b\d{4}\s\d{4}\s\d{4}\s\d{4}\b'
            ],
            "address": [
                r'\d+\s+[\w\s]+,\s*[A-Za-z]{2}\s*\d{5}',
                r'\d+\s+[\w\s]+,\s*[A-Za-z]{2}\s*\d{5}-\d{4}'
            ],
            "driver_license": [
                r'\b[A-Z]{1,2}\d{6,8}\b',
                r'\b\d{8,12}\b'
            ],
            "passport": [
                r'\b[A-Z]{1,2}\d{7,9}\b'
            ],
            "bank_account": [
                r'\b\d{9,18}\b'
            ]
        }
        
        self.privacy_violation_patterns = {
            "data_collection": [
                "collect your data", "store your information", "keep records",
                "save your details", "maintain database", "track your activity"
            ],
            "profiling": [
                "build your profile", "create your profile", "analyze your behavior",
                "track your patterns", "monitor your activity", "study your habits"
            ],
            "sharing_data": [
                "share your data", "sell your information", "third parties",
                "advertisers", "partners", "data brokers"
            ],
            "location_tracking": [
                "track your location", "gps data", "where you are",
                "your location", "geographic data", "position tracking"
            ]
        }
        
        self.privacy_protection_rules = {
            "no_data_storage": "Never store or retain user personal information",
            "no_profiling": "Never create user profiles or behavioral analysis",
            "no_tracking": "Never track user activity across sessions",
            "no_sharing": "Never share user data with third parties",
            "anonymize_data": "Anonymize any data used for system improvement",
            "minimal_collection": "Collect only essential information for immediate response"
        }
    
    def detect_pii_violations(self, text):
        """
        Detect personally identifiable information in text
        """
        violations = {
            "pii_detected": [],
            "risk_level": "LOW",
            "sanitized_text": text
        }
        
        risk_score = 0
        
        # Check for PII patterns
        for pii_type, patterns in self.pii_patterns.items():
            for pattern in patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                if matches:
                    violations["pii_detected"].append({
                        "type": pii_type,
                        "matches": matches,
                        "count": len(matches)
                    })
                    
                    # Calculate risk score
                    if pii_type in ["ssn", "credit_card", "bank_account"]:
                        risk_score += 30
                    elif pii_type in ["phone_number", "email", "address"]:
                        risk_score += 20
                    else:
                        risk_score += 10
                    
                    # Sanitize text
                    for match in matches:
                        violations["sanitized_text"] = violations["sanitized_text"].replace(
                            match, f"[{pii_type.upper()}_REDACTED]"
                        )
        
        # Determine risk level
        if risk_score >= 50:
            violations["risk_level"] = "HIGH"
        elif risk_score >= 20:
            violations["risk_level"] = "MEDIUM"
        
        return violations
    
    def detect_privacy_violations(self, text):
        """
        Detect privacy-violating language or requests
        """
        violations = {
            "privacy_issues": [],
            "severity": "LOW"
        }
        
        text_lower = text.lower()
        
        # Check for privacy violation patterns
        for category, patterns in self.privacy_violation_patterns.items():
            for pattern in patterns:
                if pattern in text_lower:
                    violations["privacy_issues"].append({
                        "category": category,
                        "pattern": pattern,
                        "severity": "MEDIUM"
                    })
        
        # Check for requests for personal data
        personal_data_requests = [
            "what is your name", "who are you", "personal information",
            "tell me about yourself", "your details", "your background"
        ]
        
        for request in personal_data_requests:
            if request in text_lower:
                violations["privacy_issues"].append({
                    "category": "personal_inquiry",
                    "pattern": request,
                    "severity": "LOW"
                })
        
        # Determine overall severity
        high_severity = any(issue["severity"] == "MEDIUM" for issue in violations["privacy_issues"])
        violations["severity"] = "HIGH" if high_severity else "LOW"
        
        return violations
    
    def create_privacy_safe_prompt(self, user_query):
        """
        Create a prompt that respects privacy boundaries
        """
        privacy_guidelines = """
PRIVACY GUIDELINES:
1. Do not request or store personal information
2. Do not create user profiles or track behavior
3. Do not ask for identifying details
4. Provide anonymous, general responses
5. Focus on the query, not the user
6. Do not collect data for any purpose

RESPONSE REQUIREMENTS:
- Be helpful while maintaining privacy
- Do not ask for personal information
- Do not suggest data collection
- Do not reference previous conversations
- Do not create user profiles

"""
        
        prompt = f"""{privacy_guidelines}
USER QUERY: {user_query}

Please provide a helpful response while strictly maintaining privacy boundaries.

RESPONSE:"""
        
        return prompt
    
    def generate_privacy_response(self, user_query):
        """
        Generate response with privacy protection
        """
        # Detect PII in user input
        pii_violations = self.detect_pii_violations(user_query)
        
        # Detect privacy violations in user input
        privacy_violations = self.detect_privacy_violations(user_query)
        
        response_info = {
            "original_query": user_query,
            "sanitized_query": pii_violations["sanitized_text"],
            "pii_violations": pii_violations["pii_detected"],
            "privacy_violations": privacy_violations["privacy_issues"],
            "risk_level": pii_violations["risk_level"],
            "response_generated": False,
            "response": "",
            "privacy_warnings": []
        }
        
        # Add privacy warnings
        if pii_violations["pii_detected"]:
            response_info["privacy_warnings"].append(
                f"🚨 PII DETECTED ({pii_violations['risk_level']} risk): {len(pii_violations['pii_detected'])} types found"
            )
        
        if privacy_violations["privacy_issues"]:
            response_info["privacy_warnings"].append(
                f"⚠️ PRIVACY ISSUES: {len(privacy_violations['privacy_issues'])} concerns detected"
            )
        
        # Determine if response should be generated
        should_respond = True
        
        # Block high-risk PII
        if pii_violations["risk_level"] == "HIGH":
            should_respond = False
            response_info["response"] = "🚨 PRIVACY ALERT: Your message contains sensitive personal information. For your privacy, please remove personal details and try again."
        
        # Provide privacy education for privacy violations
        elif privacy_violations["privacy_issues"]:
            privacy_education = """
🔒 PRIVACY PROTECTION NOTICE:
I prioritize your privacy and security:
• I don't store or collect personal information
• I don't create user profiles or track behavior
• I don't share data with third parties
• Each conversation is independent and anonymous

"""
            
            if should_respond:
                try:
                    prompt = self.create_privacy_safe_prompt(user_query)
                    response = get_completion(prompt)
                    response_info["response"] = privacy_education + "\n\n" + response
                    response_info["response_generated"] = True
                except Exception as e:
                    response_info["response"] = privacy_education + "\n\nI apologize, but I'm unable to process your request at this time."
        
        # Generate normal response
        elif should_respond:
            try:
                prompt = self.create_privacy_safe_prompt(user_query)
                response = get_completion(prompt)
                response_info["response"] = response
                response_info["response_generated"] = True
            except Exception as e:
                response_info["response"] = "I apologize, but I'm unable to process your request at this time."
        
        return response_info
    
    def create_privacy_summary(self):
        """
        Create summary of privacy protection measures
        """
        return f"""
🔒 PRIVACY PROTECTION SUMMARY

Rules Followed:
{chr(10).join(f"• {rule}" for rule in self.privacy_protection_rules.values())}

PII Detection:
• Phone numbers, emails, SSN, credit cards
• Addresses, driver licenses, passports
• Bank accounts and other identifiers
• Automatic sanitization and blocking

Privacy Violations Detected:
• Data collection requests
• User profiling attempts
• Data sharing inquiries
• Location tracking requests

Response Strategy:
• High-risk PII: Blocked with privacy alert
• Medium-risk: Education + limited response
• Low-risk: Normal response with privacy guidelines
• All responses: Privacy-first approach

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

# Test cases
test_cases = [
    {
        "name": "Normal Query - Privacy Safe",
        "query": "What are the benefits of renewable energy?"
    },
    {
        "name": "PII Detected - Phone Number",
        "query": "My phone number is 555-123-4567, can you help me with something?"
    },
    {
        "name": "PII Detected - Email",
        "query": "Contact me at john.doe@email.com for more information"
    },
    {
        "name": "PII Detected - SSN",
        "query": "My social security number is 123-45-6789, what should I do?"
    },
    {
        "name": "Privacy Violation - Data Collection",
        "query": "Can you collect my data to create a better user profile?"
    },
    {
        "name": "Privacy Violation - Tracking",
        "query": "Can you track my activity to provide better recommendations?"
    },
    {
        "name": "Personal Information Request",
        "query": "What is your name and tell me about yourself?"
    },
    {
        "name": "Multiple PII Types",
        "query": "My name is John, email is john@email.com, phone is 555-123-4567, and I live at 123 Main St, NY 10001"
    }
]

# Run privacy guardrails demo
privacy_system = PrivacyGuardrails()

print("=== Privacy Guardrails Demo ===\n")

for test_case in test_cases:
    print(f"🧪 Test: {test_case['name']}")
    print(f"📝 Query: {test_case['query']}")
    
    # Generate privacy-protected response
    response_info = privacy_system.generate_privacy_response(test_case['query'])
    
    print(f"\n📊 Privacy Analysis:")
    print(f"   Risk Level: {response_info['risk_level']}")
    print(f"   PII Detected: {len(response_info['pii_violations'])} types")
    print(f"   Privacy Issues: {len(response_info['privacy_violations'])} concerns")
    
    if response_info['privacy_warnings']:
        print(f"\n⚠️ Privacy Warnings:")
        for warning in response_info['privacy_warnings']:
            print(f"   {warning}")
    
    if response_info['pii_violations']:
        print(f"\n🔍 PII Details:")
        for pii in response_info['pii_violations']:
            print(f"   • {pii['type']}: {pii['count']} found")
    
    print(f"\n🤖 Response:")
    print(response_info['response'][:400] + "..." if len(response_info['response']) > 400 else response_info['response'])
    
    print("\n" + "="*60 + "\n")

# Show privacy summary
print(privacy_system.create_privacy_summary())
