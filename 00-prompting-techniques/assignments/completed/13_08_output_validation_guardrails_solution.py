"""
Assignment 13_08 — Output Validation Guardrails Solution
Task: Create a workflow that validates AI outputs before returning to users
"""

import sys
from pathlib import Path
import re
import json

# allow importing from project root
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from helper import get_completion

class OutputValidationGuardrails:
    """
    Validate AI outputs for quality, safety, and appropriateness before returning to users
    """
    
    def __init__(self):
        self.validation_rules = {
            "content_quality": {
                "min_length": 20,
                "max_length": 2000,
                "required_content": ["helpful", "relevant"],
                "forbidden_content": ["I cannot", "I'm unable", "error", "failed"]
            },
            "safety_checks": {
                "harmful_patterns": [
                    r'\b(kill|harm|hurt|violence|weapon)\b',
                    r'\b(suicide|self.harm|end.my.life)\b',
                    r'\b(hate|racist|discriminat)\b'
                ],
                "personal_info": [
                    r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',  # Phone
                    r'\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b',  # Credit card
                    r'\b\d{3}-\d{2}-\d{4}\b'  # SSN
                ],
                "inappropriate_language": [
                    r'\b(damn|hell|stupid|idiot)\b'
                ]
            },
            "factual_accuracy": {
                "fact_check_patterns": [
                    r'\b(always|never|everyone|nobody)\b',  # Absolutes
                    r'\b(guarantee|promise|certain)\b'  # Unverifiable claims
                ],
                "require_sources": ["statistics", "research", "study", "data"],
                "disclaimer_required": ["medical", "legal", "financial"]
            },
            "format_consistency": {
                "sentence_structure": True,
                "grammar_check": True,
                "coherence_check": True
            }
        }
        
        self.disclaimers = {
            "medical": "This is not medical advice. Please consult a healthcare professional.",
            "legal": "This is not legal advice. Please consult a qualified attorney.",
            "financial": "This is not financial advice. Please consult a professional advisor."
        }
    
    def validate_output(self, output, context="general"):
        """
        Comprehensive validation of AI output
        """
        validation_result = {
            "is_valid": True,
            "score": 100,
            "issues": [],
            "warnings": [],
            "required_actions": [],
            "validated_output": output
        }
        
        # 1. Content Quality Validation
        quality_issues = self._validate_content_quality(output)
        validation_result["issues"].extend(quality_issues)
        validation_result["score"] -= len(quality_issues) * 10
        
        # 2. Safety Validation
        safety_issues = self._validate_safety(output)
        validation_result["issues"].extend(safety_issues["critical"])
        validation_result["warnings"].extend(safety_issues["warnings"])
        validation_result["score"] -= len(safety_issues["critical"]) * 20
        
        # 3. Factual Accuracy Validation
        accuracy_issues = self._validate_factual_accuracy(output)
        validation_result["warnings"].extend(accuracy_issues)
        validation_result["score"] -= len(accuracy_issues) * 5
        
        # 4. Format Consistency Validation
        format_issues = self._validate_format(output)
        validation_result["issues"].extend(format_issues)
        validation_result["score"] -= len(format_issues) * 5
        
        # 5. Context-specific Validation
        context_actions = self._validate_context_specific(output, context)
        validation_result["required_actions"].extend(context_actions)
        
        # 6. Apply required actions
        if validation_result["required_actions"]:
            output = self._apply_required_actions(output, validation_result["required_actions"])
            validation_result["validated_output"] = output
        
        # Determine overall validity
        critical_issues = [issue for issue in validation_result["issues"] if issue.startswith("🚨")]
        validation_result["is_valid"] = len(critical_issues) == 0 and validation_result["score"] >= 60
        
        return validation_result
    
    def _validate_content_quality(self, output):
        """
        Validate content quality metrics
        """
        issues = []
        rules = self.validation_rules["content_quality"]
        
        # Length checks
        if len(output) < rules["min_length"]:
            issues.append("🚨 Response too short")
        
        if len(output) > rules["max_length"]:
            issues.append("⚠️ Response too long")
        
        # Check for unhelpful content
        for forbidden in rules["forbidden_content"]:
            if forbidden.lower() in output.lower():
                issues.append("🚨 Contains unhelpful content")
        
        # Check for empty or meaningless content
        if not output.strip() or output.strip().lower() in ["i don't know", ""]:
            issues.append("🚨 Empty response")
        
        return issues
    
    def _validate_safety(self, output):
        """
        Validate safety of content
        """
        issues = {"critical": [], "warnings": []}
        rules = self.validation_rules["safety_checks"]
        
        output_lower = output.lower()
        
        # Check harmful patterns
        for pattern in rules["harmful_patterns"]:
            if re.search(pattern, output_lower):
                issues["critical"].append("🚨 Harmful content detected")
        
        # Check personal information
        for pattern in rules["personal_info"]:
            if re.search(pattern, output):
                issues["warnings"].append("⚠️ Potential personal information detected")
        
        # Check inappropriate language
        for pattern in rules["inappropriate_language"]:
            if re.search(pattern, output_lower):
                issues["warnings"].append("⚠️ Inappropriate language detected")
        
        return issues
    
    def _validate_factual_accuracy(self, output):
        """
        Validate factual accuracy and claims
        """
        warnings = []
        rules = self.validation_rules["factual_accuracy"]
        
        output_lower = output.lower()
        
        # Check for absolute statements
        for pattern in rules["fact_check_patterns"]:
            if re.search(pattern, output_lower):
                warnings.append("⚠️ Absolute statement detected")
        
        # Check for claims requiring sources
        for keyword in rules["require_sources"]:
            if keyword in output_lower and "source" not in output_lower:
                warnings.append(f"⚠️ Claim about {keyword} without sources")
        
        return warnings
    
    def _validate_format(self, output):
        """
        Validate format consistency
        """
        issues = []
        rules = self.validation_rules["format_consistency"]
        
        # Basic sentence structure check
        sentences = output.split('.')
        if len(sentences) > 1:
            for sentence in sentences[:-1]:  # Ignore last empty sentence
                if len(sentence.strip()) < 5:
                    issues.append("⚠️ Incomplete sentence detected")
        
        # Check for excessive repetition
        words = output.split()
        if len(words) > 10:
            unique_words = set(words)
            repetition_ratio = 1 - (len(unique_words) / len(words))
            if repetition_ratio > 0.4:
                issues.append("⚠️ High repetition detected")
        
        return issues
    
    def _validate_context_specific(self, output, context):
        """
        Context-specific validation
        """
        actions = []
        
        # Check if disclaimer is needed
        for category, disclaimer in self.disclaimers.items():
            if category in output.lower() and disclaimer not in output:
                actions.append(f"add_disclaimer_{category}")
        
        return actions
    
    def _apply_required_actions(self, output, actions):
        """
        Apply required validation actions
        """
        modified_output = output
        
        for action in actions:
            if action.startswith("add_disclaimer_"):
                category = action.replace("add_disclaimer_", "")
                disclaimer = self.disclaimers.get(category)
                if disclaimer:
                    modified_output += f"\n\n{disclaimer}"
        
        return modified_output
    
    def create_validation_aware_prompt(self, user_query, context="general"):
        """
        Create prompt with validation awareness
        """
        prompt = f"""You are a helpful AI assistant. Please provide a high-quality response to this query.

QUALITY REQUIREMENTS:
- Response should be 20-2000 characters
- Be helpful and relevant
- Avoid absolute statements unless certain
- Include sources for statistical claims

SAFETY REQUIREMENTS:
- No harmful or inappropriate content
- No personal information
- Be respectful and professional

CONTEXT: {context}

USER QUERY: {user_query}

RESPONSE:"""
        
        return prompt

# Test cases
test_cases = [
    {
        "name": "Valid Response - General",
        "query": "What are the benefits of regular exercise?",
        "context": "general"
    },
    {
        "name": "Medical Context - Needs Disclaimer",
        "query": "What are common symptoms of diabetes?",
        "context": "medical"
    },
    {
        "name": "Short Response - Invalid",
        "query": "Help",
        "context": "general"
    },
    {
        "name": "Financial Context - Needs Disclaimer",
        "query": "Should I invest in stocks?",
        "context": "financial"
    },
    {
        "name": "Complex Query",
        "query": "Explain the economic impact of renewable energy adoption",
        "context": "general"
    }
]

# Run output validation guardrails demo
validation_system = OutputValidationGuardrails()

print("=== Output Validation Guardrails Demo ===\n")

for test_case in test_cases:
    print(f"🧪 Test: {test_case['name']}")
    print(f"📝 Query: {test_case['query']}")
    print(f"📋 Context: {test_case['context']}")
    
    # Generate response
    prompt = validation_system.create_validation_aware_prompt(test_case['query'], test_case['context'])
    
    try:
        response = get_completion(prompt)
        print(f"\n🤖 Raw Response:")
        print(response[:400] + "..." if len(response) > 400 else response)
        
        # Validate output
        validation_result = validation_system.validate_output(response, test_case['context'])
        
        print(f"\n📊 Validation Results:")
        print(f"   Overall Score: {validation_result['score']}/100")
        print(f"   Valid: {'✅ Yes' if validation_result['is_valid'] else '❌ No'}")
        
        if validation_result['issues']:
            print(f"\n❌ Issues:")
            for issue in validation_result['issues']:
                print(f"   {issue}")
        
        if validation_result['warnings']:
            print(f"\n⚠️ Warnings:")
            for warning in validation_result['warnings']:
                print(f"   {warning}")
        
        if validation_result['required_actions']:
            print(f"\n🔧 Actions Applied:")
            for action in validation_result['required_actions']:
                print(f"   ✅ {action}")
        
        if validation_result['validated_output'] != response:
            print(f"\n✅ Validated Output:")
            print(validation_result['validated_output'][:400] + "..." if len(validation_result['validated_output']) > 400 else validation_result['validated_output'])
        
    except Exception as e:
        print(f"\n❌ Error generating response: {e}")
    
    print("\n" + "="*60 + "\n")
