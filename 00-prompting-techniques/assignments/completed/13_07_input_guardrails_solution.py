"""
Assignment 13_07 — Input Guardrails Solution
Task: Create a workflow that checks the input before calling the model
"""

import sys
from pathlib import Path
import re

# allow importing from project root
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from helper import get_completion

class WorkplaceIncidentValidator:
    """
    Input validation for workplace incident reporting system
    """
    
    def __init__(self):
        # Define allowed incident types
        self.allowed_incident_types = [
            "injury", "illness", "near_miss", "property_damage", 
            "security", "environmental", "vehicle_accident"
        ]
        
        # Define severity levels
        self.allowed_severity_levels = ["low", "medium", "high", "critical"]
        
        # Blocked content patterns
        self.blocked_patterns = [
            r'.*test.*incident.*',  # Test entries
            r'.*fake.*',           # Fake reports
            r'.*joke.*',           # Joke entries
            r'\d{3}-\d{3}-\d{4}',  # Phone numbers (PII)
            r'\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b'  # Credit card numbers
        ]
        
        # Required fields
        self.required_fields = {
            "incident_type": "Incident type must be specified",
            "severity": "Severity level must be specified", 
            "description": "Incident description must be provided",
            "location": "Location must be specified"
        }
    
    def validate_input(self, incident_data):
        """
        Validate incident report data
        Returns (is_valid, messages)
        """
        validation_messages = []
        
        # Check required fields
        for field, error_msg in self.required_fields.items():
            if field not in incident_data or not incident_data[field].strip():
                validation_messages.append(f"❌ Missing required field: {field}")
        
        # Validate incident type
        if "incident_type" in incident_data:
            incident_type = incident_data["incident_type"].lower()
            if incident_type not in self.allowed_incident_types:
                validation_messages.append(f"❌ Invalid incident type: '{incident_type}'. Allowed types: {', '.join(self.allowed_incident_types)}")
        
        # Validate severity level
        if "severity" in incident_data:
            severity = incident_data["severity"].lower()
            if severity not in self.allowed_severity_levels:
                validation_messages.append(f"❌ Invalid severity level: '{severity}'. Allowed levels: {', '.join(self.allowed_severity_levels)}")
        
        # Check for blocked content
        combined_text = " ".join(incident_data.values()).lower()
        for pattern in self.blocked_patterns:
            if re.search(pattern, combined_text, re.IGNORECASE):
                validation_messages.append(f"❌ Blocked content detected: {pattern}")
        
        # Check description length
        if "description" in incident_data:
            desc_length = len(incident_data["description"])
            if desc_length < 20:
                validation_messages.append("❌ Description too short (minimum 20 characters)")
            elif desc_length > 2000:
                validation_messages.append("❌ Description too long (maximum 2000 characters)")
        
        # Check for potential emergency indicators
        emergency_keywords = ["emergency", "life threatening", "911", "ambulance", "immediate danger"]
        if any(keyword in combined_text for keyword in emergency_keywords):
            validation_messages.append("⚠️  This appears to be an emergency. Please contact emergency services immediately.")
        
        is_valid = len([msg for msg in validation_messages if msg.startswith("❌")]) == 0
        
        if is_valid:
            validation_messages.append("✅ Input validation passed")
        
        return is_valid, validation_messages

def create_incident_prompt(incident_data):
    """
    Create prompt for incident analysis
    """
    prompt = f"""
You are an AI assistant for workplace incident analysis. Analyze the following incident report:

Incident Type: {incident_data.get('incident_type', 'Not specified')}
Severity: {incident_data.get('severity', 'Not specified')}
Location: {incident_data.get('location', 'Not specified')}
Description: {incident_data.get('description', 'Not specified')}
Date/Time: {incident_data.get('datetime', 'Not specified')}

Please provide:
1. Risk assessment
2. Recommended immediate actions
3. Suggested preventive measures
4. Whether this requires escalation

IMPORTANT: This is for informational purposes only. Follow your company's official incident reporting procedures.
"""
    
    return prompt

# Test cases
test_cases = [
    {
        "name": "Valid Incident Report",
        "data": {
            "incident_type": "injury",
            "severity": "medium",
            "description": "Employee slipped on wet floor in break room and sprained wrist. Floor was recently mopped but no wet floor sign was present.",
            "location": "Break room, 2nd floor",
            "datetime": "2024-01-15 14:30"
        },
        "expected": "valid"
    },
    {
        "name": "Missing Required Fields",
        "data": {
            "incident_type": "injury",
            "description": "Employee got hurt"
        },
        "expected": "invalid"
    },
    {
        "name": "Invalid Incident Type",
        "data": {
            "incident_type": "alien_invasion",
            "severity": "high",
            "description": "Spaceship landed in parking lot",
            "location": "Parking lot"
        },
        "expected": "invalid"
    },
    {
        "name": "Blocked Content",
        "data": {
            "incident_type": "injury",
            "severity": "low",
            "description": "This is just a test incident for demonstration purposes",
            "location": "Office"
        },
        "expected": "invalid"
    },
    {
        "name": "Emergency Indicators",
        "data": {
            "incident_type": "injury",
            "severity": "critical",
            "description": "Employee collapsed and appears life threatening, need ambulance immediately",
            "location": "Production floor"
        },
        "expected": "warning"
    }
]

# Run validation demo
validator = WorkplaceIncidentValidator()

print("=== Input Guardrails Demo: Workplace Incident Reporting ===\n")

for test_case in test_cases:
    print(f"🧪 Test: {test_case['name']}")
    print(f"📋 Input Data: {test_case['data']}")
    
    is_valid, messages = validator.validate_input(test_case['data'])
    
    print("\n📊 Validation Results:")
    for message in messages:
        print(f"   {message}")
    
    # Only call model if validation passes (and no emergency warnings)
    if is_valid and not any("emergency" in msg.lower() for msg in messages):
        print("\n🤖 Model Response:")
        prompt = create_incident_prompt(test_case['data'])
        try:
            response = get_completion(prompt)
            print(response[:400] + "..." if len(response) > 400 else response)
        except Exception as e:
            print(f"Error calling model: {e}")
    
    print("\n" + "="*60 + "\n")
