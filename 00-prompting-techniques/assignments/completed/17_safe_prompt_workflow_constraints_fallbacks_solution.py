"""
Assignment 17 — Safe Prompt Workflow with Constraints and Fallbacks Solution
Task: Create a comprehensive safe prompt workflow with constraints and fallback mechanisms
"""

import sys
import json
import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from enum import Enum

# allow importing from project root
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from helper import get_completion

class SafetyLevel(Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class WorkflowStatus(Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    BLOCKED = "BLOCKED"
    ESCALATED = "ESCALATED"
    FAILED = "FAILED"

class SafePromptWorkflowSystem:
    """
    Comprehensive safe prompt workflow with constraints and fallback mechanisms
    """
    
    def __init__(self):
        self.workflow_config = {
            "max_execution_time": 30,  # seconds
            "max_retries": 3,
            "strict_mode": False,
            "enable_all_safety_checks": True,
            "log_all_activities": True,
            "require_human_approval_for_critical": True
        }
        
        self.safety_constraints = {
            "content_filters": {
                "violence": ["kill", "harm", "violence", "weapon", "attack"],
                "self_harm": ["suicide", "kill myself", "self harm", "end my life"],
                "hate_speech": ["hate", "racist", "discriminat", "supremacist"],
                "illegal": ["illegal", "crime", "hack", "fraud", "steal"],
                "explicit": ["pornographic", "sexual", "explicit content"]
            },
            "privacy_filters": {
                "pii_patterns": [
                    r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',  # Phone
                    r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Email
                    r'\b\d{3}-\d{2}-\d{4}\b',  # SSN
                    r'\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b'  # Credit card
                ]
            },
            "scope_limitations": {
                "medical": ["diagnosis", "prescribe", "treatment plan", "medical advice"],
                "legal": ["legal advice", "represent client", "case strategy"],
                "financial": ["specific investment advice", "guaranteed returns", "market prediction"]
            }
        }
        
        self.fallback_strategies = {
            "content_violation": {
                "response": "I apologize, but I cannot process this request as it may contain inappropriate content.",
                "escalation": False,
                "retry": False
            },
            "privacy_violation": {
                "response": "For your privacy and security, please remove personal information and try again.",
                "escalation": False,
                "retry": True
            },
            "scope_violation": {
                "response": "This request is outside my scope. Let me help with something else or suggest alternative resources.",
                "escalation": True,
                "retry": False
            },
            "emergency_situation": {
                "response": "🚨 This appears to be an emergency. Please call 911 or seek immediate help.",
                "escalation": True,
                "retry": False
            },
            "api_failure": {
                "response": "I'm experiencing technical difficulties. Please try again in a moment.",
                "escalation": False,
                "retry": True
            },
            "timeout": {
                "response": "The request took too long to process. Please try with a shorter query.",
                "escalation": False,
                "retry": False
            }
        }
        
        self.workflow_steps = [
            "input_preprocessing",
            "safety_validation",
            "privacy_check",
            "scope_verification",
            "prompt_construction",
            "api_execution",
            "response_validation",
            "output_postprocessing"
        ]
        
        self.execution_history = []
        self.performance_metrics = {
            "total_workflows": 0,
            "completed_workflows": 0,
            "blocked_workflows": 0,
            "escalated_workflows": 0,
            "failed_workflows": 0,
            "average_execution_time": 0,
            "safety_violations": 0,
            "privacy_violations": 0,
            "fallback_usage": {}
        }
    
    def execute_safe_workflow(self, user_input: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Execute complete safe workflow with constraints and fallbacks
        """
        if context is None:
            context = {"user_role": "general", "application": "general"}
        
        workflow_id = self._generate_workflow_id()
        start_time = datetime.now()
        
        workflow_result = {
            "workflow_id": workflow_id,
            "timestamp": start_time.isoformat(),
            "user_input": user_input,
            "context": context,
            "status": WorkflowStatus.PENDING.value,
            "safety_level": SafetyLevel.LOW.value,
            "steps_completed": [],
            "violations": [],
            "fallback_used": None,
            "final_response": "",
            "execution_time": 0,
            "retry_count": 0,
            "escalation_triggered": False
        }
        
        try:
            # Step 1: Input Preprocessing
            step_result = self._step_input_preprocessing(user_input)
            workflow_result["steps_completed"].append(step_result)
            
            if not step_result["success"]:
                return self._complete_workflow(workflow_result, WorkflowStatus.BLOCKED, "Input preprocessing failed")
            
            # Step 2: Safety Validation
            step_result = self._step_safety_validation(step_result["processed_input"])
            workflow_result["steps_completed"].append(step_result)
            workflow_result["safety_level"] = step_result["safety_level"]
            
            if step_result["violations"]:
                workflow_result["violations"].extend(step_result["violations"])
                
                # Handle critical safety violations
                if step_result["safety_level"] == SafetyLevel.CRITICAL:
                    return self._handle_critical_violation(workflow_result, step_result)
            
            # Step 3: Privacy Check
            step_result = self._step_privacy_check(step_result["processed_input"])
            workflow_result["steps_completed"].append(step_result)
            
            if step_result["privacy_violations"]:
                workflow_result["violations"].extend(step_result["privacy_violations"])
                
                if step_result["risk_level"] == "HIGH":
                    return self._handle_privacy_violation(workflow_result, step_result)
            
            # Step 4: Scope Verification
            step_result = self._step_scope_verification(step_result["processed_input"], context)
            workflow_result["steps_completed"].append(step_result)
            
            if not step_result["in_scope"]:
                return self._handle_scope_violation(workflow_result, step_result)
            
            # Step 5: Prompt Construction
            step_result = self._step_prompt_construction(step_result["processed_input"], context)
            workflow_result["steps_completed"].append(step_result)
            
            # Step 6: API Execution (with retry mechanism)
            step_result = self._step_api_execution_with_retry(step_result["prompt"], workflow_result)
            workflow_result["steps_completed"].append(step_result)
            
            if not step_result["success"]:
                return self._handle_api_failure(workflow_result, step_result)
            
            # Step 7: Response Validation
            step_result = self._step_response_validation(step_result["response"])
            workflow_result["steps_completed"].append(step_result)
            
            if not step_result["valid"]:
                return self._handle_response_validation_failure(workflow_result, step_result)
            
            # Step 8: Output Postprocessing
            step_result = self._step_output_postprocessing(step_result["validated_response"])
            workflow_result["steps_completed"].append(step_result)
            
            # Complete successfully
            workflow_result["final_response"] = step_result["final_output"]
            return self._complete_workflow(workflow_result, WorkflowStatus.COMPLETED)
            
        except Exception as e:
            workflow_result["violations"].append(f"System error: {str(e)}")
            return self._complete_workflow(workflow_result, WorkflowStatus.FAILED, f"System error: {str(e)}")
        
        finally:
            # Calculate execution time
            end_time = datetime.now()
            workflow_result["execution_time"] = (end_time - start_time).total_seconds()
            
            # Update metrics
            self._update_performance_metrics(workflow_result)
            
            # Log workflow
            if self.workflow_config["log_all_activities"]:
                self.execution_history.append(workflow_result.copy())
    
    def _step_input_preprocessing(self, user_input: str) -> Dict[str, Any]:
        """Step 1: Input preprocessing"""
        step_result = {
            "step": "input_preprocessing",
            "success": True,
            "processed_input": user_input.strip(),
            "original_length": len(user_input),
            "processed_length": len(user_input.strip()),
            "issues": []
        }
        
        # Length validation
        if len(step_result["processed_input"]) < 3:
            step_result["success"] = False
            step_result["issues"].append("Input too short")
        elif len(step_result["processed_input"]) > 5000:
            step_result["success"] = False
            step_result["issues"].append("Input too long")
        
        # Content validation
        if not step_result["processed_input"]:
            step_result["success"] = False
            step_result["issues"].append("Empty input after processing")
        
        return step_result
    
    def _step_safety_validation(self, processed_input: str) -> Dict[str, Any]:
        """Step 2: Safety validation"""
        step_result = {
            "step": "safety_validation",
            "success": True,
            "safety_level": SafetyLevel.LOW.value,
            "violations": [],
            "emergency_detected": False
        }
        
        input_lower = processed_input.lower()
        risk_score = 0
        
        # Check content filters
        for category, keywords in self.safety_constraints["content_filters"].items():
            for keyword in keywords:
                if keyword in input_lower:
                    step_result["violations"].append(f"Content violation: {category}")
                    
                    # Calculate risk based on category
                    if category in ["self_harm", "violence"]:
                        risk_score += 30
                        if category == "self_harm":
                            step_result["emergency_detected"] = True
                    elif category in ["hate_speech", "illegal"]:
                        risk_score += 20
                    else:
                        risk_score += 10
        
        # Determine safety level
        if risk_score >= 30:
            step_result["safety_level"] = SafetyLevel.CRITICAL.value
            step_result["success"] = False
        elif risk_score >= 20:
            step_result["safety_level"] = SafetyLevel.HIGH.value
        elif risk_score >= 10:
            step_result["safety_level"] = SafetyLevel.MEDIUM.value
        
        return step_result
    
    def _step_privacy_check(self, processed_input: str) -> Dict[str, Any]:
        """Step 3: Privacy check"""
        step_result = {
            "step": "privacy_check",
            "success": True,
            "privacy_violations": [],
            "risk_level": "LOW",
            "sanitized_input": processed_input
        }
        
        # Check PII patterns
        pii_detected = []
        for pattern in self.safety_constraints["privacy_filters"]["pii_patterns"]:
            matches = re.findall(pattern, processed_input)
            if matches:
                pii_detected.extend(matches)
        
        if pii_detected:
            step_result["privacy_violations"] = [f"PII detected: {len(pii_detected)} instances"]
            step_result["risk_level"] = "HIGH"
            
            # Sanitize input
            for match in pii_detected:
                step_result["sanitized_input"] = step_result["sanitized_input"].replace(match, "[REDACTED]")
        
        return step_result
    
    def _step_scope_verification(self, processed_input: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Step 4: Scope verification"""
        step_result = {
            "step": "scope_verification",
            "success": True,
            "in_scope": True,
            "scope_violations": [],
            "application": context.get("application", "general")
        }
        
        application = context.get("application", "general")
        input_lower = processed_input.lower()
        
        # Check scope limitations
        if application in self.safety_constraints["scope_limitations"]:
            limitations = self.safety_constraints["scope_limitations"][application]
            for limitation in limitations:
                if limitation in input_lower:
                    step_result["scope_violations"].append(f"Scope violation: {limitation}")
                    step_result["in_scope"] = False
        
        return step_result
    
    def _step_prompt_construction(self, processed_input: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Step 5: Prompt construction"""
        step_result = {
            "step": "prompt_construction",
            "success": True,
            "prompt": "",
            "safety_guidelines_added": True
        }
        
        # Construct safe prompt
        safety_guidelines = """
SAFETY GUIDELINES:
1. Provide helpful, accurate, and safe responses
2. Do not engage with harmful or inappropriate content
3. Maintain professional and respectful communication
4. Do not provide medical, legal, or financial advice
5. Protect user privacy and confidentiality
6. Escalate if emergency situations are detected

RESPONSE REQUIREMENTS:
- Be clear and informative
- Stay within appropriate boundaries
- Include disclaimers when necessary
- Do not make unsupported claims

"""
        
        prompt = f"""{safety_guidelines}
USER QUERY: {processed_input}
CONTEXT: {context}

SAFE RESPONSE:"""
        
        step_result["prompt"] = prompt
        
        return step_result
    
    def _step_api_execution_with_retry(self, prompt: str, workflow_result: Dict[str, Any]) -> Dict[str, Any]:
        """Step 6: API execution with retry mechanism"""
        step_result = {
            "step": "api_execution",
            "success": False,
            "response": "",
            "attempts": 0,
            "errors": []
        }
        
        max_retries = self.workflow_config["max_retries"]
        
        for attempt in range(max_retries + 1):
            try:
                step_result["attempts"] = attempt + 1
                
                # Check timeout
                if workflow_result["execution_time"] > self.workflow_config["max_execution_time"]:
                    raise TimeoutError("Workflow execution timeout")
                
                response = get_completion(prompt)
                
                if response and response.strip():
                    step_result["success"] = True
                    step_result["response"] = response
                    workflow_result["retry_count"] = attempt
                    break
                else:
                    raise ValueError("Empty response from API")
            
            except Exception as e:
                step_result["errors"].append(f"Attempt {attempt + 1}: {str(e)}")
                
                if attempt < max_retries:
                    continue
                else:
                    # All retries failed
                    break
        
        return step_result
    
    def _step_response_validation(self, response: str) -> Dict[str, Any]:
        """Step 7: Response validation"""
        step_result = {
            "step": "response_validation",
            "success": True,
            "valid": True,
            "validated_response": response,
            "issues": []
        }
        
        # Length validation
        if len(response) < 10:
            step_result["valid"] = False
            step_result["issues"].append("Response too short")
        
        # Content validation
        error_indicators = ["i cannot", "unable to", "error", "sorry"]
        if any(indicator in response.lower() for indicator in error_indicators):
            step_result["issues"].append("Error indicators in response")
        
        # Safety validation
        response_lower = response.lower()
        for category, keywords in self.safety_constraints["content_filters"].items():
            for keyword in keywords:
                if keyword in response_lower:
                    step_result["valid"] = False
                    step_result["issues"].append(f"Unsafe content in response: {category}")
        
        return step_result
    
    def _step_output_postprocessing(self, validated_response: str) -> Dict[str, Any]:
        """Step 8: Output postprocessing"""
        step_result = {
            "step": "output_postprocessing",
            "success": True,
            "final_output": validated_response,
            "modifications": []
        }
        
        # Add safety disclaimer if needed
        if any(word in validated_response.lower() for word in ["medical", "health", "symptom"]):
            disclaimer = "\n\nNote: This is not medical advice. Please consult a healthcare professional."
            step_result["final_output"] += disclaimer
            step_result["modifications"].append("Added medical disclaimer")
        
        if any(word in validated_response.lower() for word in ["legal", "law", "court"]):
            disclaimer = "\n\nNote: This is not legal advice. Please consult a qualified attorney."
            step_result["final_output"] += disclaimer
            step_result["modifications"].append("Added legal disclaimer")
        
        return step_result
    
    def _handle_critical_violation(self, workflow_result: Dict[str, Any], step_result: Dict[str, Any]) -> Dict[str, Any]:
        """Handle critical safety violations"""
        workflow_result["status"] = WorkflowStatus.ESCALATED.value
        workflow_result["escalation_triggered"] = True
        
        # Use emergency fallback
        fallback = self.fallback_strategies["emergency_situation"]
        workflow_result["final_response"] = fallback["response"]
        workflow_result["fallback_used"] = "emergency_situation"
        
        return self._complete_workflow(workflow_result, WorkflowStatus.ESCALATED, "Critical safety violation")
    
    def _handle_privacy_violation(self, workflow_result: Dict[str, Any], step_result: Dict[str, Any]) -> Dict[str, Any]:
        """Handle privacy violations"""
        fallback = self.fallback_strategies["privacy_violation"]
        workflow_result["final_response"] = fallback["response"]
        workflow_result["fallback_used"] = "privacy_violation"
        
        return self._complete_workflow(workflow_result, WorkflowStatus.BLOCKED, "Privacy violation")
    
    def _handle_scope_violation(self, workflow_result: Dict[str, Any], step_result: Dict[str, Any]) -> Dict[str, Any]:
        """Handle scope violations"""
        fallback = self.fallback_strategies["scope_violation"]
        workflow_result["final_response"] = fallback["response"]
        workflow_result["fallback_used"] = "scope_violation"
        
        if fallback["escalation"]:
            workflow_result["escalation_triggered"] = True
            return self._complete_workflow(workflow_result, WorkflowStatus.ESCALATED, "Scope violation - escalation needed")
        else:
            return self._complete_workflow(workflow_result, WorkflowStatus.BLOCKED, "Scope violation")
    
    def _handle_api_failure(self, workflow_result: Dict[str, Any], step_result: Dict[str, Any]) -> Dict[str, Any]:
        """Handle API failures"""
        fallback = self.fallback_strategies["api_failure"]
        workflow_result["final_response"] = fallback["response"]
        workflow_result["fallback_used"] = "api_failure"
        
        return self._complete_workflow(workflow_result, WorkflowStatus.FAILED, "API failure")
    
    def _handle_response_validation_failure(self, workflow_result: Dict[str, Any], step_result: Dict[str, Any]) -> Dict[str, Any]:
        """Handle response validation failures"""
        workflow_result["final_response"] = "I apologize, but I'm unable to provide a complete response at this time."
        workflow_result["fallback_used"] = "response_validation_failure"
        
        return self._complete_workflow(workflow_result, WorkflowStatus.FAILED, "Response validation failed")
    
    def _complete_workflow(self, workflow_result: Dict[str, Any], status: WorkflowStatus, reason: str = "") -> Dict[str, Any]:
        """Complete workflow with final status"""
        workflow_result["status"] = status.value
        if reason:
            workflow_result["completion_reason"] = reason
        
        return workflow_result
    
    def _generate_workflow_id(self) -> str:
        """Generate unique workflow ID"""
        return f"WORKFLOW_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash(datetime.now().isoformat()) % 10000:04d}"
    
    def _update_performance_metrics(self, workflow_result: Dict[str, Any]) -> None:
        """Update performance metrics"""
        self.performance_metrics["total_workflows"] += 1
        
        status = workflow_result["status"]
        if status == WorkflowStatus.COMPLETED.value:
            self.performance_metrics["completed_workflows"] += 1
        elif status == WorkflowStatus.BLOCKED.value:
            self.performance_metrics["blocked_workflows"] += 1
        elif status == WorkflowStatus.ESCALATED.value:
            self.performance_metrics["escalated_workflows"] += 1
        elif status == WorkflowStatus.FAILED.value:
            self.performance_metrics["failed_workflows"] += 1
        
        # Update safety violations
        if workflow_result["violations"]:
            self.performance_metrics["safety_violations"] += len(workflow_result["violations"])
        
        # Update fallback usage
        if workflow_result["fallback_used"]:
            fallback_type = workflow_result["fallback_used"]
            if fallback_type not in self.performance_metrics["fallback_usage"]:
                self.performance_metrics["fallback_usage"][fallback_type] = 0
            self.performance_metrics["fallback_usage"][fallback_type] += 1
        
        # Update average execution time
        total_time = self.performance_metrics["average_execution_time"] * (self.performance_metrics["total_workflows"] - 1)
        total_time += workflow_result["execution_time"]
        self.performance_metrics["average_execution_time"] = total_time / self.performance_metrics["total_workflows"]
    
    def get_workflow_summary(self) -> Dict[str, Any]:
        """Get workflow execution summary"""
        total = self.performance_metrics["total_workflows"]
        if total == 0:
            return {"message": "No workflows executed"}
        
        return {
            "total_workflows": total,
            "completion_rate": f"{(self.performance_metrics['completed_workflows'] / total) * 100:.1f}%",
            "block_rate": f"{(self.performance_metrics['blocked_workflows'] / total) * 100:.1f}%",
            "escalation_rate": f"{(self.performance_metrics['escalated_workflows'] / total) * 100:.1f}%",
            "failure_rate": f"{(self.performance_metrics['failed_workflows'] / total) * 100:.1f}%",
            "average_execution_time": f"{self.performance_metrics['average_execution_time']:.3f}s",
            "safety_violations": self.performance_metrics["safety_violations"],
            "fallback_usage": self.performance_metrics["fallback_usage"]
        }

# Test cases
test_cases = [
    {
        "name": "Normal Query - Should Complete",
        "query": "What are the benefits of renewable energy?",
        "context": {"user_role": "general", "application": "general"}
    },
    {
        "name": "Emergency Situation - Should Escalate",
        "query": "I'm having suicidal thoughts and need help immediately",
        "context": {"user_role": "general", "application": "general"}
    },
    {
        "name": "Privacy Violation - Should Block",
        "query": "My email is john@example.com and my phone is 555-123-4567",
        "context": {"user_role": "general", "application": "general"}
    },
    {
        "name": "Scope Violation - Medical Advice",
        "query": "Can you diagnose my headache and prescribe medication?",
        "context": {"user_role": "general", "application": "medical"}
    },
    {
        "name": "Harmful Content - Should Block",
        "query": "How can I make a weapon at home?",
        "context": {"user_role": "general", "application": "general"}
    },
    {
        "name": "Legal Scope Violation",
        "query": "I need legal advice for my court case tomorrow",
        "context": {"user_role": "general", "application": "legal"}
    },
    {
        "name": "Complex Query - Should Complete",
        "query": "Explain the impact of artificial intelligence on modern business operations and society",
        "context": {"user_role": "general", "application": "general"}
    },
    {
        "name": "Empty Input - Should Block",
        "query": "",
        "context": {"user_role": "general", "application": "general"}
    }
]

# Run safe prompt workflow demo
workflow_system = SafePromptWorkflowSystem()

print("=== Safe Prompt Workflow with Constraints and Fallbacks Demo ===\n")

for test_case in test_cases:
    print(f"🧪 Test: {test_case['name']}")
    print(f"📝 Query: {test_case['query']}")
    print(f"📋 Context: {test_case['context']}")
    
    # Execute safe workflow
    result = workflow_system.execute_safe_workflow(test_case['query'], test_case['context'])
    
    print(f"\n📊 Workflow Results:")
    print(f"   Workflow ID: {result['workflow_id']}")
    print(f"   Status: {result['status']}")
    print(f"   Safety Level: {result['safety_level']}")
    print(f"   Execution Time: {result['execution_time']:.3f}s")
    print(f"   Steps Completed: {len(result['steps_completed'])}")
    print(f"   Retry Count: {result['retry_count']}")
    print(f"   Escalation Triggered: {'Yes' if result['escalation_triggered'] else 'No'}")
    
    if result['violations']:
        print(f"\n❌ Violations:")
        for violation in result['violations']:
            print(f"   • {violation}")
    
    if result['fallback_used']:
        print(f"\n🔄 Fallback Used: {result['fallback_used']}")
    
    print(f"\n📋 Workflow Steps:")
    for step in result['steps_completed']:
        status = "✅" if step.get("success", True) else "❌"
        step_name = step['step'].replace('_', ' ').title()
        print(f"   {status} {step_name}")
        
        # Show step details
        if 'safety_level' in step:
            print(f"      Safety Level: {step['safety_level']}")
        if 'violations' in step and step['violations']:
            print(f"      Violations: {len(step['violations'])}")
        if 'privacy_violations' in step and step['privacy_violations']:
            print(f"      Privacy Issues: {len(step['privacy_violations'])}")
        if 'in_scope' in step and not step['in_scope']:
            print(f"      Scope: OUT OF SCOPE")
        if 'attempts' in step:
            print(f"      Attempts: {step['attempts']}")
        if 'valid' in step and not step['valid']:
            print(f"      Validation: FAILED")
    
    print(f"\n🤖 Final Response:")
    response = result['final_response']
    print(response[:400] + "..." if len(response) > 400 else response)
    
    print("\n" + "="*60 + "\n")

# Show workflow summary
print(f"\n📊 Workflow Summary:")
summary = workflow_system.get_workflow_summary()
for key, value in summary.items():
    if key != "fallback_usage":
        print(f"   {key.replace('_', ' ').title()}: {value}")

if summary.get("fallback_usage"):
    print(f"   Fallback Usage: {summary['fallback_usage']}")

print(f"\n🔧 System Configuration:")
for key, value in workflow_system.workflow_config.items():
    print(f"   {key.replace('_', ' ').title()}: {value}")
