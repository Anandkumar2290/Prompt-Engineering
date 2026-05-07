"""
Assignment 16 — JSON Prompting and API Reliability Solution
Task: Create reliable JSON-structured outputs with API reliability patterns
"""

import sys
import json
import re
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

# allow importing from project root
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from helper import get_completion

class JSONPromptingReliabilitySystem:
    """
    System for reliable JSON prompting with API reliability patterns
    """
    
    def __init__(self):
        self.json_schemas = {
            "analysis_result": {
                "type": "object",
                "required": ["status", "confidence", "data", "timestamp"],
                "properties": {
                    "status": {"type": "string", "enum": ["success", "error", "partial"]},
                    "confidence": {"type": "number", "minimum": 0, "maximum": 1},
                    "data": {"type": "object"},
                    "timestamp": {"type": "string"},
                    "metadata": {"type": "object", "optional": True}
                }
            },
            "product_info": {
                "type": "object",
                "required": ["product_id", "name", "category", "price", "features"],
                "properties": {
                    "product_id": {"type": "string"},
                    "name": {"type": "string"},
                    "category": {"type": "string"},
                    "price": {"type": "object", "properties": {"amount": {"type": "number"}, "currency": {"type": "string"}}},
                    "features": {"type": "array", "items": {"type": "string"}},
                    "availability": {"type": "string", "enum": ["in_stock", "out_of_stock", "limited"]},
                    "rating": {"type": "number", "minimum": 0, "maximum": 5, "optional": True}
                }
            },
            "sentiment_analysis": {
                "type": "object",
                "required": ["text", "sentiment", "confidence", "emotions"],
                "properties": {
                    "text": {"type": "string"},
                    "sentiment": {"type": "string", "enum": ["positive", "negative", "neutral"]},
                    "confidence": {"type": "number", "minimum": 0, "maximum": 1},
                    "emotions": {"type": "array", "items": {"type": "string"}},
                    "key_phrases": {"type": "array", "items": {"type": "string"}, "optional": True},
                    "analysis_metadata": {"type": "object", "optional": True}
                }
            }
        }
        
        self.reliability_patterns = {
            "retry_mechanism": {
                "max_retries": 3,
                "backoff_strategy": "exponential",
                "retry_conditions": ["json_parse_error", "schema_validation_error", "api_timeout"]
            },
            "fallback_responses": {
                "json_parse_error": '{"status": "error", "error": "JSON parsing failed", "fallback": true}',
                "schema_validation_error": '{"status": "error", "error": "Schema validation failed", "fallback": true}',
                "api_error": '{"status": "error", "error": "API call failed", "fallback": true}',
                "empty_response": '{"status": "error", "error": "Empty response received", "fallback": true}'
            },
            "validation_rules": {
                "required_fields": "check_all_required_fields_present",
                "data_types": "validate_field_data_types",
                "value_ranges": "check_value_constraints",
                "enum_values": "verify_enum_compliance"
            },
            "error_handling": {
                "graceful_degradation": "provide_partial_results_when_possible",
                "error_logging": "log_all_errors_for_monitoring",
                "user_feedback": "provide_clear_error_messages"
            }
        }
        
        self.performance_metrics = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "retry_attempts": 0,
            "fallback_used": 0,
            "average_response_time": 0,
            "error_types": {}
        }
    
    def create_json_prompt(self, user_query: str, schema_name: str, 
                          additional_instructions: str = "") -> str:
        """
        Create a robust JSON prompt with schema validation
        """
        schema = self.json_schemas.get(schema_name)
        if not schema:
            raise ValueError(f"Unknown schema: {schema_name}")
        
        # Generate schema description
        schema_description = self._generate_schema_description(schema)
        
        prompt = f"""You are a JSON data processing assistant. Your task is to process the user's request and return a valid JSON response.

CRITICAL REQUIREMENTS:
1. Your ENTIRE response must be valid JSON only
2. No additional text, explanations, or markdown formatting
3. Follow the exact schema provided below
4. Include all required fields
5. Use proper data types as specified

JSON SCHEMA:
{schema_description}

USER REQUEST:
{user_query}

{additional_instructions}

RESPONSE (JSON ONLY):"""
        
        return prompt
    
    def _generate_schema_description(self, schema: Dict[str, Any]) -> str:
        """
        Generate human-readable schema description
        """
        description_parts = []
        
        description_parts.append(f"Type: {schema['type']}")
        
        if 'required' in schema:
            description_parts.append(f"Required fields: {', '.join(schema['required'])}")
        
        description_parts.append("Properties:")
        for prop_name, prop_config in schema['properties'].items():
            prop_type = prop_config['type']
            required_marker = " (REQUIRED)" if prop_name in schema.get('required', []) else " (OPTIONAL)"
            
            if prop_type == "object":
                description_parts.append(f"  - {prop_name}{required_marker}: Object with nested properties")
            elif prop_type == "array":
                item_type = prop_config.get('items', {}).get('type', 'string')
                description_parts.append(f"  - {prop_name}{required_marker}: Array of {item_type}s")
            elif "enum" in prop_config:
                enum_values = ", ".join(prop_config['enum'])
                description_parts.append(f"  - {prop_name}{required_marker}: String, must be one of: {enum_values}")
            elif "minimum" in prop_config or "maximum" in prop_config:
                min_val = prop_config.get('minimum', 'N/A')
                max_val = prop_config.get('maximum', 'N/A')
                description_parts.append(f"  - {prop_name}{required_marker}: Number, range: {min_val}-{max_val}")
            else:
                description_parts.append(f"  - {prop_name}{required_marker}: {prop_type}")
        
        return "\n".join(description_parts)
    
    def validate_json_response(self, response: str, schema_name: str) -> Dict[str, Any]:
        """
        Validate JSON response against schema
        """
        validation_result = {
            "is_valid": False,
            "parsed_data": None,
            "errors": [],
            "warnings": [],
            "completeness": 0
        }
        
        # Step 1: Parse JSON
        try:
            parsed_data = json.loads(response)
            validation_result["parsed_data"] = parsed_data
        except json.JSONDecodeError as e:
            validation_result["errors"].append(f"JSON parsing error: {str(e)}")
            return validation_result
        
        # Step 2: Validate schema
        schema = self.json_schemas.get(schema_name)
        if not schema:
            validation_result["errors"].append(f"Unknown schema: {schema_name}")
            return validation_result
        
        # Validate required fields
        required_fields = schema.get("required", [])
        missing_fields = [field for field in required_fields if field not in parsed_data]
        
        if missing_fields:
            validation_result["errors"].append(f"Missing required fields: {', '.join(missing_fields)}")
        
        # Validate field types and constraints
        properties = schema.get("properties", {})
        for field_name, field_config in properties.items():
            if field_name in parsed_data:
                field_value = parsed_data[field_name]
                field_type = field_config.get("type")
                
                # Type validation
                if not self._validate_field_type(field_value, field_type, field_config):
                    validation_result["errors"].append(f"Type mismatch for field '{field_name}': expected {field_type}")
                
                # Enum validation
                if "enum" in field_config and field_value not in field_config["enum"]:
                    validation_result["errors"].append(f"Invalid value for field '{field_name}': must be one of {field_config['enum']}")
                
                # Range validation
                if field_type == "number":
                    if "minimum" in field_config and field_value < field_config["minimum"]:
                        validation_result["errors"].append(f"Value for field '{field_name}' below minimum: {field_config['minimum']}")
                    if "maximum" in field_config and field_value > field_config["maximum"]:
                        validation_result["errors"].append(f"Value for field '{field_name}' above maximum: {field_config['maximum']}")
        
        # Check for unexpected fields
        allowed_fields = set(properties.keys())
        actual_fields = set(parsed_data.keys())
        unexpected_fields = actual_fields - allowed_fields
        
        if unexpected_fields:
            validation_result["warnings"].append(f"Unexpected fields: {', '.join(unexpected_fields)}")
        
        # Calculate completeness
        if required_fields:
            present_required = [field for field in required_fields if field in parsed_data]
            validation_result["completeness"] = len(present_required) / len(required_fields)
        else:
            validation_result["completeness"] = 1.0
        
        # Final validation result
        validation_result["is_valid"] = len(validation_result["errors"]) == 0
        
        return validation_result
    
    def _validate_field_type(self, value: Any, expected_type: str, field_config: Dict[str, Any]) -> bool:
        """
        Validate field type
        """
        if expected_type == "string":
            return isinstance(value, str)
        elif expected_type == "number":
            return isinstance(value, (int, float))
        elif expected_type == "boolean":
            return isinstance(value, bool)
        elif expected_type == "array":
            return isinstance(value, list)
        elif expected_type == "object":
            return isinstance(value, dict)
        else:
            return True  # Unknown type, assume valid
    
    def execute_with_reliability(self, user_query: str, schema_name: str, 
                               additional_instructions: str = "") -> Dict[str, Any]:
        """
        Execute JSON request with reliability patterns
        """
        execution_result = {
            "request_id": self._generate_request_id(),
            "timestamp": datetime.now().isoformat(),
            "user_query": user_query,
            "schema_name": schema_name,
            "success": False,
            "final_response": None,
            "validation_result": None,
            "retry_count": 0,
            "fallback_used": False,
            "execution_time": 0,
            "errors": []
        }
        
        start_time = datetime.now()
        self.performance_metrics["total_requests"] += 1
        
        # Execute with retry mechanism
        max_retries = self.reliability_patterns["retry_mechanism"]["max_retries"]
        
        for attempt in range(max_retries + 1):
            try:
                # Create prompt
                prompt = self.create_json_prompt(user_query, schema_name, additional_instructions)
                
                # Call API
                response = get_completion(prompt)
                
                if not response.strip():
                    raise ValueError("Empty response from API")
                
                # Validate response
                validation = self.validate_json_response(response, schema_name)
                execution_result["validation_result"] = validation
                
                if validation["is_valid"]:
                    execution_result["success"] = True
                    execution_result["final_response"] = validation["parsed_data"]
                    self.performance_metrics["successful_requests"] += 1
                    break
                else:
                    # Validation failed, try retry
                    if attempt < max_retries:
                        self.performance_metrics["retry_attempts"] += 1
                        execution_result["retry_count"] += 1
                        continue
                    else:
                        # All retries failed, use fallback
                        fallback_key = self._determine_fallback_key(validation["errors"])
                        fallback_response = self.reliability_patterns["fallback_responses"][fallback_key]
                        
                        execution_result["final_response"] = json.loads(fallback_response)
                        execution_result["fallback_used"] = True
                        execution_result["errors"] = validation["errors"]
                        self.performance_metrics["fallback_used"] += 1
                        self.performance_metrics["failed_requests"] += 1
                        break
            
            except Exception as e:
                error_type = type(e).__name__
                execution_result["errors"].append(f"API error: {str(e)}")
                
                # Track error types
                if error_type not in self.performance_metrics["error_types"]:
                    self.performance_metrics["error_types"][error_type] = 0
                self.performance_metrics["error_types"][error_type] += 1
                
                if attempt < max_retries:
                    self.performance_metrics["retry_attempts"] += 1
                    execution_result["retry_count"] += 1
                    continue
                else:
                    # Use fallback for API errors
                    fallback_response = self.reliability_patterns["fallback_responses"]["api_error"]
                    execution_result["final_response"] = json.loads(fallback_response)
                    execution_result["fallback_used"] = True
                    self.performance_metrics["fallback_used"] += 1
                    self.performance_metrics["failed_requests"] += 1
                    break
        
        # Calculate execution time
        end_time = datetime.now()
        execution_result["execution_time"] = (end_time - start_time).total_seconds()
        
        # Update performance metrics
        self._update_performance_metrics(execution_result)
        
        return execution_result
    
    def _determine_fallback_key(self, errors: List[str]) -> str:
        """
        Determine appropriate fallback response based on errors
        """
        error_str = " ".join(errors).lower()
        
        if "json parsing" in error_str:
            return "json_parse_error"
        elif "schema validation" in error_str:
            return "schema_validation_error"
        elif "empty response" in error_str:
            return "empty_response"
        else:
            return "api_error"
    
    def _generate_request_id(self) -> str:
        """Generate unique request ID"""
        return f"JSON_REQ_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash(datetime.now().isoformat()) % 10000:04d}"
    
    def _update_performance_metrics(self, execution_result: Dict[str, Any]) -> None:
        """Update performance metrics"""
        # Update average response time
        total_time = self.performance_metrics["average_response_time"] * (self.performance_metrics["total_requests"] - 1)
        total_time += execution_result["execution_time"]
        self.performance_metrics["average_response_time"] = total_time / self.performance_metrics["total_requests"]
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary"""
        total = self.performance_metrics["total_requests"]
        if total == 0:
            return {"message": "No requests processed"}
        
        return {
            "total_requests": total,
            "success_rate": f"{(self.performance_metrics['successful_requests'] / total) * 100:.1f}%",
            "failure_rate": f"{(self.performance_metrics['failed_requests'] / total) * 100:.1f}%",
            "retry_rate": f"{(self.performance_metrics['retry_attempts'] / total) * 100:.1f}%",
            "fallback_rate": f"{(self.performance_metrics['fallback_used'] / total) * 100:.1f}%",
            "average_response_time": f"{self.performance_metrics['average_response_time']:.3f}s",
            "error_breakdown": self.performance_metrics["error_types"]
        }

# Test cases
test_cases = [
    {
        "name": "Product Analysis - Simple Schema",
        "query": "Analyze this product: Wireless Bluetooth Headphones with noise cancellation, $199, currently in stock",
        "schema": "product_info"
    },
    {
        "name": "Sentiment Analysis - Complex Schema",
        "query": "I absolutely love this new phone! The camera is amazing and the battery life is incredible. Best purchase ever!",
        "schema": "sentiment_analysis"
    },
    {
        "name": "General Analysis - Flexible Schema",
        "query": "Evaluate the business proposal for expanding into European markets",
        "schema": "analysis_result"
    },
    {
        "name": "Invalid Query - Should Use Fallback",
        "query": "",  # Empty query to trigger error
        "schema": "product_info"
    },
    {
        "name": "Complex Query - Multiple Retries",
        "query": "Create detailed analysis of: 'The impact of artificial intelligence on global economic markets including specific projections for the next decade, considering technological advancements, regulatory changes, and market adoption patterns across different industries and geographic regions'",
        "schema": "analysis_result"
    }
]

# Run JSON prompting and API reliability demo
json_system = JSONPromptingReliabilitySystem()

print("=== JSON Prompting and API Reliability Demo ===\n")

for test_case in test_cases:
    print(f"🧪 Test: {test_case['name']}")
    print(f"📝 Query: {test_case['query']}")
    print(f"📋 Schema: {test_case['schema']}")
    
    # Execute with reliability
    result = json_system.execute_with_reliability(
        test_case['query'], 
        test_case['schema'],
        "Focus on accuracy and completeness"
    )
    
    print(f"\n📊 Execution Results:")
    print(f"   Request ID: {result['request_id']}")
    print(f"   Success: {'✅ Yes' if result['success'] else '❌ No'}")
    print(f"   Execution Time: {result['execution_time']:.3f}s")
    print(f"   Retry Count: {result['retry_count']}")
    print(f"   Fallback Used: {'Yes' if result['fallback_used'] else 'No'}")
    
    if result['validation_result']:
        validation = result['validation_result']
        print(f"   Validation: {'✅ Passed' if validation['is_valid'] else '❌ Failed'}")
        print(f"   Completeness: {validation['completeness']*100:.0f}%")
        
        if validation['errors']:
            print(f"   Errors: {', '.join(validation['errors'][:2])}")  # Show first 2 errors
    
    if result['errors']:
        print(f"   System Errors: {len(result['errors'])} errors")
    
    print(f"\n🤖 Final Response:")
    if result['final_response']:
        response_json = json.dumps(result['final_response'], indent=2)
        print(response_json[:400] + "..." if len(response_json) > 400 else response_json)
    else:
        print("   No response generated")
    
    print("\n" + "="*60 + "\n")

# Show performance summary
print(f"\n📊 Performance Summary:")
summary = json_system.get_performance_summary()
for key, value in summary.items():
    if key != "error_breakdown":
        print(f"   {key.replace('_', ' ').title()}: {value}")

if summary.get("error_breakdown"):
    print(f"   Error Types: {summary['error_breakdown']}")
