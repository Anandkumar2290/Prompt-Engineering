"""
Assignment 13_12 — Tool/Action Guardrails Solution
Task: Create a workflow that validates and controls AI tool usage and actions
"""

import sys
from pathlib import Path
import re
import json
from datetime import datetime

# allow importing from project root
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from helper import get_completion

class ToolActionGuardrails:
    """
    Validate and control AI tool usage and actions
    """
    
    def __init__(self):
        self.tool_categories = {
            "data_access": {
                "tools": ["database_query", "file_read", "api_call", "web_search"],
                "risk_level": "MEDIUM",
                "required_permissions": ["read_access"],
                "validation_rules": ["check_data_sensitivity", "verify_access_rights"]
            },
            "data_modification": {
                "tools": ["database_write", "file_write", "api_post", "data_update"],
                "risk_level": "HIGH",
                "required_permissions": ["write_access", "admin_approval"],
                "validation_rules": ["backup_required", "change_tracking", "approval_workflow"]
            },
            "system_operations": {
                "tools": ["system_command", "process_control", "service_restart", "config_change"],
                "risk_level": "CRITICAL",
                "required_permissions": ["system_admin", "multi_factor_auth"],
                "validation_rules": ["safety_check", "rollback_plan", "impact_assessment"]
            },
            "communication": {
                "tools": ["send_email", "send_sms", "post_notification", "api_webhook"],
                "risk_level": "MEDIUM",
                "required_permissions": ["communication_access"],
                "validation_rules": ["content_filter", "recipient_verify", "spam_check"]
            },
            "external_integrations": {
                "tools": ["third_party_api", "payment_process", "external_service"],
                "risk_level": "HIGH",
                "required_permissions": ["integration_access", "compliance_check"],
                "validation_rules": ["vendor_trust", "data_protection", "rate_limit"]
            }
        }
        
        self.action_restrictions = {
            "blocked_actions": [
                "delete_all", "format_drive", "shutdown_system", "disable_security",
                "export_all_data", "modify_permissions", "access_sensitive_data"
            ],
            "require_approval": [
                "bulk_operations", "schema_changes", "production_deployments",
                "financial_transactions", "legal_documents", "customer_communications"
            ],
            "time_restricted": [
                "system_maintenance", "data_migrations", "security_updates",
                "performance_optimization", "backup_operations"
            ],
            "audit_required": [
                "data_access", "configuration_changes", "user_management",
                "permission_changes", "log_access", "audit_operations"
            ]
        }
        
        self.safety_protocols = {
            "pre_action_checks": [
                "verify_user_intent", "check_permissions", "assess_impact",
                "validate_parameters", "check_dependencies"
            ],
            "post_actions": [
                "log_action", "verify_result", "update_audit_trail",
                "notify_stakeholders", "cleanup_resources"
            ],
            "emergency_stops": [
                "safety_violation", "permission_denied", "system_error",
                "resource_exhaustion", "security_breach"
            ]
        }
    
    def parse_tool_action_request(self, user_input):
        """
        Parse user input to identify requested tool/action
        """
        action_patterns = {
            "database_query": [
                r"query.*database", r"select.*from", r"get.*data", r"search.*records"
            ],
            "file_write": [
                r"write.*file", r"save.*to", r"create.*file", r"export.*to"
            ],
            "file_read": [
                r"read.*file", r"open.*file", r"load.*from", r"import.*from"
            ],
            "send_email": [
                r"send.*email", r"email.*to", r"mail.*to", r"notify.*by.*email"
            ],
            "api_call": [
                r"call.*api", r"make.*request", r"fetch.*from.*api", r"api.*call"
            ],
            "system_command": [
                r"run.*command", r"execute.*command", r"system.*command", r"shell.*command"
            ],
            "delete_data": [
                r"delete.*data", r"remove.*records", r"drop.*table", r"clear.*data"
            ],
            "update_config": [
                r"update.*config", r"change.*settings", r"modify.*config", r"config.*change"
            ]
        }
        
        detected_actions = []
        input_lower = user_input.lower()
        
        for action, patterns in action_patterns.items():
            for pattern in patterns:
                if re.search(pattern, input_lower):
                    detected_actions.append(action)
                    break
        
        return detected_actions
    
    def validate_tool_action(self, action, parameters, user_context):
        """
        Validate if tool action is allowed and safe
        """
        validation_result = {
            "allowed": True,
            "risk_level": "LOW",
            "requirements": [],
            "warnings": [],
            "block_reasons": [],
            "safety_checks": []
        }
        
        # Check if action is blocked
        if any(blocked in action for blocked in ["delete", "remove", "drop", "clear"]):
            if any(blocked in action for blocked in self.action_restrictions["blocked_actions"]):
                validation_result["allowed"] = False
                validation_result["block_reasons"].append("Action is blocked for security reasons")
                validation_result["risk_level"] = "CRITICAL"
        
        # Determine tool category and risk
        tool_category = self._get_tool_category(action)
        if tool_category:
            category_info = self.tool_categories[tool_category]
            validation_result["risk_level"] = category_info["risk_level"]
            validation_result["requirements"] = category_info["required_permissions"]
        
        # Check for approval requirements
        if any(restricted in action for restricted in self.action_restrictions["require_approval"]):
            validation_result["warnings"].append("Action requires approval before execution")
        
        # Check for time restrictions
        if any(restricted in action for restricted in self.action_restrictions["time_restricted"]):
            validation_result["warnings"].append("Action is time-restricted (maintenance window)")
        
        # Perform safety checks
        safety_results = self._perform_safety_checks(action, parameters)
        validation_result["safety_checks"] = safety_results
        
        if not all(safety_results.values()):
            validation_result["allowed"] = False
            validation_result["block_reasons"].append("Safety checks failed")
        
        return validation_result
    
    def _get_tool_category(self, action):
        """
        Determine tool category for action
        """
        for category, info in self.tool_categories.items():
            if action in info["tools"]:
                return category
        return None
    
    def _perform_safety_checks(self, action, parameters):
        """
        Perform safety checks on action
        """
        checks = {}
        
        # Parameter validation
        checks["parameters_valid"] = self._validate_parameters(parameters)
        
        # User intent verification
        checks["intent_verified"] = self._verify_user_intent(action)
        
        # Resource availability
        checks["resources_available"] = self._check_resources(action)
        
        # Security compliance
        checks["security_compliant"] = self._check_security_compliance(action)
        
        return checks
    
    def _validate_parameters(self, parameters):
        """
        Validate action parameters
        """
        if not parameters:
            return True  # No parameters to validate
        
        # Check for dangerous parameters
        dangerous_patterns = [
            r"rm\s+-rf", r"format\s+c:", r"delete\s+all", r"drop\s+all"
        ]
        
        param_str = str(parameters).lower()
        for pattern in dangerous_patterns:
            if re.search(pattern, param_str):
                return False
        
        return True
    
    def _verify_user_intent(self, action):
        """
        Verify user intent is legitimate
        """
        # Basic intent verification - in real system, this would be more sophisticated
        suspicious_actions = ["delete_all", "format_drive", "shutdown_system"]
        
        if action in suspicious_actions:
            return False
        
        return True
    
    def _check_resources(self, action):
        """
        Check if required resources are available
        """
        # Simulated resource check
        resource_intensive_actions = ["bulk_operations", "data_migrations", "system_maintenance"]
        
        if action in resource_intensive_actions:
            # In real system, check actual resource availability
            return True  # Assume resources available for demo
        
        return True
    
    def _check_security_compliance(self, action):
        """
        Check security compliance
        """
        # Basic security compliance check
        non_compliant_actions = ["disable_security", "bypass_auth", "access_sensitive_data"]
        
        if action in non_compliant_actions:
            return False
        
        return True
    
    def create_action_execution_plan(self, action, parameters, validation_result):
        """
        Create execution plan for validated action
        """
        if not validation_result["allowed"]:
            return {
                "executable": False,
                "plan": "Action blocked due to safety/security concerns",
                "next_steps": ["Review action requirements", "Obtain necessary permissions"]
            }
        
        plan = {
            "executable": True,
            "action": action,
            "parameters": parameters,
            "risk_level": validation_result["risk_level"],
            "execution_steps": [],
            "safety_measures": [],
            "monitoring_required": validation_result["risk_level"] in ["HIGH", "CRITICAL"]
        }
        
        # Generate execution steps
        plan["execution_steps"] = self._generate_execution_steps(action)
        
        # Add safety measures
        plan["safety_measures"] = self._generate_safety_measures(validation_result)
        
        return plan
    
    def _generate_execution_steps(self, action):
        """
        Generate execution steps for action
        """
        base_steps = [
            "1. Pre-execution validation",
            "2. Resource preparation",
            "3. Action execution",
            "4. Result verification",
            "5. Post-execution cleanup"
        ]
        
        # Add action-specific steps
        if "database" in action:
            base_steps.insert(2, "2.5. Database connection setup")
        elif "file" in action:
            base_steps.insert(2, "2.5. File system access verification")
        elif "api" in action:
            base_steps.insert(2, "2.5. API authentication setup")
        
        return base_steps
    
    def _generate_safety_measures(self, validation_result):
        """
        Generate safety measures based on validation
        """
        measures = ["Action logging enabled", "Error handling active"]
        
        if validation_result["risk_level"] == "HIGH":
            measures.extend(["Backup created", "Rollback plan prepared"])
        elif validation_result["risk_level"] == "CRITICAL":
            measures.extend(["Full system backup", "Emergency stop ready", "Admin notification sent"])
        
        return measures
    
    def simulate_tool_action(self, user_input, user_context):
        """
        Simulate complete tool action workflow
        """
        workflow_result = {
            "user_input": user_input,
            "detected_actions": [],
            "validation_results": [],
            "execution_plans": [],
            "final_status": "PENDING"
        }
        
        # Parse actions
        detected_actions = self.parse_tool_action_request(user_input)
        workflow_result["detected_actions"] = detected_actions
        
        if not detected_actions:
            workflow_result["final_status"] = "NO_ACTION_DETECTED"
            return workflow_result
        
        # Validate each action
        for action in detected_actions:
            # Simulate parameters (in real system, these would be extracted from input)
            parameters = {"simulated": True, "source": "user_input"}
            
            validation = self.validate_tool_action(action, parameters, user_context)
            workflow_result["validation_results"].append(validation)
            
            # Create execution plan
            plan = self.create_action_execution_plan(action, parameters, validation)
            workflow_result["execution_plans"].append(plan)
        
        # Determine final status
        if all(plan["executable"] for plan in workflow_result["execution_plans"]):
            workflow_result["final_status"] = "READY_TO_EXECUTE"
        else:
            workflow_result["final_status"] = "BLOCKED"
        
        return workflow_result

# Test cases
test_cases = [
    {
        "name": "Safe Database Query",
        "query": "Can you query the customer database to get user information?"
    },
    {
        "name": "Potentially Dangerous File Operation",
        "query": "Delete all files in the system directory"
    },
    {
        "name": "System Command Request",
        "query": "Run a system command to restart the web server"
    },
    {
        "name": "Email Communication",
        "query": "Send an email notification to all users about system maintenance"
    },
    {
        "name": "API Integration",
        "query": "Make an API call to the payment processor to process a refund"
    },
    {
        "name": "Configuration Change",
        "query": "Update the system configuration to disable security features"
    },
    {
        "name": "Data Export",
        "query": "Export all customer data to a CSV file"
    },
    {
        "name": "Normal Query - No Tools",
        "query": "What is the weather like today?"
    }
]

# Run tool/action guardrails demo
tool_system = ToolActionGuardrails()

print("=== Tool/Action Guardrails Demo ===\n")

for test_case in test_cases:
    print(f"🧪 Test: {test_case['name']}")
    print(f"📝 Query: {test_case['query']}")
    
    # Simulate tool action workflow
    workflow_result = tool_system.simulate_tool_action(test_case['query'], {"user": "demo_user"})
    
    print(f"\n📊 Workflow Results:")
    print(f"   Status: {workflow_result['final_status']}")
    print(f"   Actions Detected: {len(workflow_result['detected_actions'])}")
    
    if workflow_result['detected_actions']:
        for i, action in enumerate(workflow_result['detected_actions']):
            validation = workflow_result['validation_results'][i]
            plan = workflow_result['execution_plans'][i]
            
            print(f"\n   Action {i+1}: {action}")
            print(f"   Risk Level: {validation['risk_level']}")
            print(f"   Allowed: {'✅ Yes' if validation['allowed'] else '❌ No'}")
            
            if validation['block_reasons']:
                print(f"   Block Reasons: {', '.join(validation['block_reasons'])}")
            
            if validation['warnings']:
                print(f"   Warnings: {', '.join(validation['warnings'])}")
            
            if validation['requirements']:
                print(f"   Requirements: {', '.join(validation['requirements'])}")
            
            if plan['executable']:
                print(f"   Execution Steps: {len(plan['execution_steps'])} steps")
                print(f"   Safety Measures: {len(plan['safety_measures'])} measures")
                print(f"   Monitoring Required: {'Yes' if plan['monitoring_required'] else 'No'}")
    
    print("\n" + "="*60 + "\n")
