"""
Assignment 13_13 — Combined Guardrail Workflow Solution
Task: Create a comprehensive workflow combining multiple guardrail types
"""

import sys
from pathlib import Path
import re
import json
from datetime import datetime
from typing import Dict, List, Any

# allow importing from project root
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from helper import get_completion

class CombinedGuardrailWorkflow:
    """
    Comprehensive workflow combining all guardrail types
    """
    
    def __init__(self):
        # Initialize all guardrail components
        self.input_validator = InputGuardrails()
        self.scope_validator = ScopeGuardrails()
        self.safety_validator = SafetyGuardrails()
        self.behavior_validator = BehaviorGuardrails()
        self.output_validator = OutputGuardrails()
        self.escalation_system = EscalationSystem()
        self.privacy_protector = PrivacyGuardrails()
        self.tool_controller = ToolActionGuardrails()
        
        self.workflow_config = {
            "enable_all_guardrails": True,
            "strict_mode": False,
            "log_all_checks": True,
            "require_human_approval": False,
            "max_execution_time": 30  # seconds
        }
        
        self.execution_log = []
    
    def process_request(self, user_input: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Process user request through comprehensive guardrail workflow
        """
        if context is None:
            context = {"user_role": "general", "application": "general"}
        
        workflow_result = {
            "request_id": self._generate_request_id(),
            "timestamp": datetime.now().isoformat(),
            "user_input": user_input,
            "context": context,
            "workflow_steps": [],
            "final_decision": "ALLOW",
            "final_response": "",
            "guardrail_violations": [],
            "escalation_triggered": False,
            "execution_time": 0
        }
        
        start_time = datetime.now()
        
        try:
            # Step 1: Input Validation
            step_result = self._step_input_validation(user_input)
            workflow_result["workflow_steps"].append(step_result)
            
            if not step_result["passed"]:
                workflow_result["final_decision"] = "BLOCK_INPUT"
                workflow_result["guardrail_violations"].extend(step_result["violations"])
                return workflow_result
            
            # Step 2: Privacy Check
            step_result = self._step_privacy_check(user_input)
            workflow_result["workflow_steps"].append(step_result)
            
            if step_result["risk_level"] == "HIGH":
                workflow_result["final_decision"] = "BLOCK_PRIVACY"
                workflow_result["guardrail_violations"].extend(step_result["violations"])
                return workflow_result
            
            # Step 3: Safety Check
            step_result = self._step_safety_check(user_input)
            workflow_result["workflow_steps"].append(step_result)
            
            if step_result["emergency_detected"]:
                workflow_result["escalation_triggered"] = True
                workflow_result["final_decision"] = "ESCALATE"
                workflow_result["final_response"] = step_result["emergency_response"]
                return workflow_result
            
            if not step_result["passed"]:
                workflow_result["final_decision"] = "BLOCK_SAFETY"
                workflow_result["guardrail_violations"].extend(step_result["violations"])
                return workflow_result
            
            # Step 4: Scope Validation
            step_result = self._step_scope_validation(user_input, context)
            workflow_result["workflow_steps"].append(step_result)
            
            if not step_result["passed"]:
                workflow_result["final_decision"] = "BLOCK_SCOPE"
                workflow_result["guardrail_violations"].extend(step_result["violations"])
                return workflow_result
            
            # Step 5: Behavior Control
            step_result = self._step_behavior_control(user_input, context)
            workflow_result["workflow_steps"].append(step_result)
            
            if not step_result["passed"]:
                workflow_result["final_decision"] = "BLOCK_BEHAVIOR"
                workflow_result["guardrail_violations"].extend(step_result["violations"])
                return workflow_result
            
            # Step 6: Tool/Action Check
            step_result = self._step_tool_action_check(user_input)
            workflow_result["workflow_steps"].append(step_result)
            
            if not step_result["passed"]:
                workflow_result["final_decision"] = "BLOCK_TOOLS"
                workflow_result["guardrail_violations"].extend(step_result["violations"])
                return workflow_result
            
            # Step 7: Generate AI Response
            step_result = self._step_generate_response(user_input, context)
            workflow_result["workflow_steps"].append(step_result)
            
            if not step_result["success"]:
                workflow_result["final_decision"] = "ERROR_GENERATION"
                workflow_result["final_response"] = "I apologize, but I'm unable to process your request at this time."
                return workflow_result
            
            # Step 8: Output Validation
            step_result = self._step_output_validation(step_result["response"])
            workflow_result["workflow_steps"].append(step_result)
            
            if not step_result["passed"]:
                workflow_result["final_decision"] = "BLOCK_OUTPUT"
                workflow_result["guardrail_violations"].extend(step_result["violations"])
                workflow_result["final_response"] = step_result["fallback_response"]
                return workflow_result
            
            # All checks passed
            workflow_result["final_decision"] = "ALLOW"
            workflow_result["final_response"] = step_result["validated_response"]
            
        except Exception as e:
            workflow_result["final_decision"] = "ERROR"
            workflow_result["final_response"] = "An error occurred while processing your request."
            workflow_result["error"] = str(e)
        
        finally:
            end_time = datetime.now()
            workflow_result["execution_time"] = (end_time - start_time).total_seconds()
            
            # Log execution
            self._log_execution(workflow_result)
        
        return workflow_result
    
    def _step_input_validation(self, user_input: str) -> Dict[str, Any]:
        """Step 1: Input Validation"""
        violations = []
        
        # Length check
        if len(user_input) < 3:
            violations.append("Input too short")
        elif len(user_input) > 5000:
            violations.append("Input too long")
        
        # Content check
        if not user_input.strip():
            violations.append("Empty input")
        
        return {
            "step": "input_validation",
            "passed": len(violations) == 0,
            "violations": violations,
            "details": f"Input length: {len(user_input)} characters"
        }
    
    def _step_privacy_check(self, user_input: str) -> Dict[str, Any]:
        """Step 2: Privacy Check"""
        # Simulate PII detection
        pii_patterns = {
            "phone": r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
            "email": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            "ssn": r'\b\d{3}-\d{2}-\d{4}\b'
        }
        
        detected_pii = []
        for pii_type, pattern in pii_patterns.items():
            if re.search(pattern, user_input):
                detected_pii.append(pii_type)
        
        risk_level = "HIGH" if detected_pii else "LOW"
        
        return {
            "step": "privacy_check",
            "passed": risk_level != "HIGH",
            "violations": [f"PII detected: {pii}" for pii in detected_pii],
            "risk_level": risk_level,
            "details": f"PII types detected: {detected_pii}"
        }
    
    def _step_safety_check(self, user_input: str) -> Dict[str, Any]:
        """Step 3: Safety Check"""
        emergency_keywords = ["suicide", "kill myself", "emergency", "life threatening"]
        harmful_keywords = ["violence", "weapon", "harm", "attack"]
        
        emergency_detected = any(keyword in user_input.lower() for keyword in emergency_keywords)
        harmful_detected = any(keyword in user_input.lower() for keyword in harmful_keywords)
        
        violations = []
        if harmful_detected:
            violations.append("Harmful content detected")
        
        emergency_response = ""
        if emergency_detected:
            emergency_response = "🚨 If you're in crisis, please call 988 or seek immediate help. You're not alone."
        
        return {
            "step": "safety_check",
            "passed": not harmful_detected and not emergency_detected,
            "violations": violations,
            "emergency_detected": emergency_detected,
            "emergency_response": emergency_response,
            "details": f"Emergency: {emergency_detected}, Harmful: {harmful_detected}"
        }
    
    def _step_scope_validation(self, user_input: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Step 4: Scope Validation"""
        # Simulate scope checking based on context
        application = context.get("application", "general")
        
        out_of_scope_patterns = {
            "customer_service": ["legal advice", "medical advice", "financial planning"],
            "medical": ["legal advice", "financial advice", "product recommendations"],
            "financial": ["medical advice", "legal advice", "therapeutic counseling"]
        }
        
        violations = []
        patterns = out_of_scope_patterns.get(application, [])
        
        for pattern in patterns:
            if pattern in user_input.lower():
                violations.append(f"Out of scope: {pattern}")
        
        return {
            "step": "scope_validation",
            "passed": len(violations) == 0,
            "violations": violations,
            "details": f"Application: {application}, Scope violations: {len(violations)}"
        }
    
    def _step_behavior_control(self, user_input: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Step 5: Behavior Control"""
        # Simulate behavior control
        inappropriate_patterns = ["casual chat", "personal questions", "emotional support"]
        
        violations = []
        for pattern in inappropriate_patterns:
            if pattern in user_input.lower():
                violations.append(f"Inappropriate behavior: {pattern}")
        
        return {
            "step": "behavior_control",
            "passed": len(violations) == 0,
            "violations": violations,
            "details": f"Behavior violations: {len(violations)}"
        }
    
    def _step_tool_action_check(self, user_input: str) -> Dict[str, Any]:
        """Step 6: Tool/Action Check"""
        # Simulate tool action detection
        tool_patterns = [
            r"run.*command", r"execute.*script", r"delete.*data",
            r"modify.*system", r"access.*database", r"send.*email"
        ]
        
        detected_tools = []
        for pattern in tool_patterns:
            if re.search(pattern, user_input.lower()):
                detected_tools.append(pattern)
        
        violations = []
        if detected_tools:
            violations.append("Tool action detected - requires special handling")
        
        return {
            "step": "tool_action_check",
            "passed": len(detected_tools) == 0,  # Block tool actions in demo
            "violations": violations,
            "detected_tools": detected_tools,
            "details": f"Tools detected: {detected_tools}"
        }
    
    def _step_generate_response(self, user_input: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Step 7: Generate AI Response"""
        try:
            # Create safety-aware prompt
            prompt = f"""You are a helpful AI assistant. Provide a safe, helpful, and appropriate response.

USER QUERY: {user_input}

GUIDELINES:
- Be helpful and informative
- Maintain appropriate boundaries
- Do not provide harmful or inappropriate content
- Keep response professional and respectful

RESPONSE:"""
            
            response = get_completion(prompt)
            
            return {
                "step": "generate_response",
                "success": True,
                "response": response,
                "details": f"Response generated: {len(response)} characters"
            }
        
        except Exception as e:
            return {
                "step": "generate_response",
                "success": False,
                "error": str(e),
                "details": "Failed to generate response"
            }
    
    def _step_output_validation(self, response: str) -> Dict[str, Any]:
        """Step 8: Output Validation"""
        violations = []
        
        # Length check
        if len(response) < 10:
            violations.append("Response too short")
        elif len(response) > 4000:
            violations.append("Response too long")
        
        # Content check
        error_indicators = ["i cannot", "unable to", "error", "sorry"]
        if any(indicator in response.lower() for indicator in error_indicators):
            violations.append("Error indicators in response")
        
        # Fallback response
        fallback_response = "I apologize, but I'm unable to provide a complete response to your request. Please try rephrasing your question."
        
        return {
            "step": "output_validation",
            "passed": len(violations) == 0,
            "violations": violations,
            "validated_response": response,
            "fallback_response": fallback_response,
            "details": f"Output violations: {len(violations)}"
        }
    
    def _generate_request_id(self) -> str:
        """Generate unique request ID"""
        return f"REQ_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash(datetime.now().isoformat()) % 10000:04d}"
    
    def _log_execution(self, workflow_result: Dict[str, Any]) -> None:
        """Log workflow execution"""
        log_entry = {
            "request_id": workflow_result["request_id"],
            "timestamp": workflow_result["timestamp"],
            "final_decision": workflow_result["final_decision"],
            "execution_time": workflow_result["execution_time"],
            "violations_count": len(workflow_result["guardrail_violations"]),
            "escalation_triggered": workflow_result["escalation_triggered"]
        }
        
        self.execution_log.append(log_entry)
    
    def get_workflow_summary(self) -> Dict[str, Any]:
        """Get summary of workflow executions"""
        if not self.execution_log:
            return {"message": "No executions logged"}
        
        total_requests = len(self.execution_log)
        blocked_requests = sum(1 for log in self.execution_log if log["final_decision"].startswith("BLOCK"))
        escalated_requests = sum(1 for log in self.execution_log if log["escalation_triggered"])
        avg_execution_time = sum(log["execution_time"] for log in self.execution_log) / total_requests
        
        return {
            "total_requests": total_requests,
            "blocked_requests": blocked_requests,
            "escalated_requests": escalated_requests,
            "block_rate": f"{(blocked_requests/total_requests)*100:.1f}%",
            "escalation_rate": f"{(escalated_requests/total_requests)*100:.1f}%",
            "avg_execution_time": f"{avg_execution_time:.3f}s",
            "recent_requests": self.execution_log[-5:]  # Last 5 requests
        }

# Simplified guardrail classes for demo (in real implementation, these would be the full classes)
class InputGuardrails:
    def validate(self, input_text): return {"passed": True, "violations": []}

class ScopeGuardrails:
    def validate(self, input_text, context): return {"passed": True, "violations": []}

class SafetyGuardrails:
    def check(self, input_text): return {"passed": True, "emergency": False}

class BehaviorGuardrails:
    def validate(self, input_text, context): return {"passed": True, "violations": []}

class OutputGuardrails:
    def validate(self, response): return {"passed": True, "violations": []}

class EscalationSystem:
    def check(self, input_text): return {"escalate": False, "reason": ""}

class PrivacyGuardrails:
    def check(self, input_text): return {"risk": "LOW", "violations": []}

class ToolActionGuardrails:
    def validate(self, input_text): return {"passed": True, "violations": []}

# Test cases
test_cases = [
    {
        "name": "Normal Query - Should Pass",
        "query": "What are the benefits of renewable energy?",
        "context": {"user_role": "general", "application": "general"}
    },
    {
        "name": "PII Detected - Should Block",
        "query": "My phone number is 555-123-4567, can you help me?",
        "context": {"user_role": "general", "application": "general"}
    },
    {
        "name": "Emergency - Should Escalate",
        "query": "I'm having suicidal thoughts and need help",
        "context": {"user_role": "general", "application": "general"}
    },
    {
        "name": "Harmful Content - Should Block",
        "query": "How can I make a weapon at home?",
        "context": {"user_role": "general", "application": "general"}
    },
    {
        "name": "Tool Action - Should Block",
        "query": "Run a system command to delete all files",
        "context": {"user_role": "general", "application": "general"}
    },
    {
        "name": "Out of Scope - Should Block",
        "query": "Can you provide legal advice for my court case?",
        "context": {"user_role": "general", "application": "customer_service"}
    },
    {
        "name": "Long Query - Should Pass",
        "query": "Can you explain in detail the process of photosynthesis including all the chemical reactions, the role of chlorophyll, the importance of sunlight, and how this process contributes to the global ecosystem?",
        "context": {"user_role": "general", "application": "general"}
    }
]

# Run combined guardrail workflow demo
workflow_system = CombinedGuardrailWorkflow()

print("=== Combined Guardrail Workflow Demo ===\n")

for test_case in test_cases:
    print(f"🧪 Test: {test_case['name']}")
    print(f"📝 Query: {test_case['query']}")
    print(f"📋 Context: {test_case['context']}")
    
    # Process through comprehensive workflow
    result = workflow_system.process_request(test_case['query'], test_case['context'])
    
    print(f"\n📊 Workflow Results:")
    print(f"   Request ID: {result['request_id']}")
    print(f"   Final Decision: {result['final_decision']}")
    print(f"   Execution Time: {result['execution_time']:.3f}s")
    print(f"   Steps Completed: {len(result['workflow_steps'])}")
    
    if result['guardrail_violations']:
        print(f"\n❌ Guardrail Violations:")
        for violation in result['guardrail_violations']:
            print(f"   • {violation}")
    
    if result['escalation_triggered']:
        print(f"\n🚨 Escalation Triggered")
    
    print(f"\n📋 Workflow Steps:")
    for step in result['workflow_steps']:
        status = "✅" if step.get("passed", True) else "❌"
        print(f"   {status} {step['step'].replace('_', ' ').title()}: {step.get('details', 'N/A')}")
    
    print(f"\n🤖 Final Response:")
    response = result['final_response']
    print(response[:300] + "..." if len(response) > 300 else response)
    
    print("\n" + "="*60 + "\n")

# Show workflow summary
print(f"\n📊 Workflow Summary:")
summary = workflow_system.get_workflow_summary()
for key, value in summary.items():
    if key != "recent_requests":
        print(f"   {key.replace('_', ' ').title()}: {value}")
