"""
Assignment 13_05 — Output Format Guardrails Solution
Task: Create a workflow that enforces specific output formats
"""

import sys
from pathlib import Path
import json
import re
import xml.etree.ElementTree as ET

# allow importing from project root
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from helper import get_completion

class OutputFormatGuardrails:
    """
    Enforce specific output formats for AI responses
    """
    
    def __init__(self):
        self.format_definitions = {
            "json": {
                "required_structure": {
                    "status": "string",
                    "message": "string", 
                    "data": "object/array",
                    "timestamp": "string"
                },
                "validation_rules": [
                    "must_be_valid_json",
                    "all_required_fields_present",
                    "no_extra_fields"
                ]
            },
            "xml": {
                "required_structure": {
                    "root_element": "response",
                    "required_elements": ["status", "message", "data"]
                },
                "validation_rules": [
                    "must_be_valid_xml",
                    "all_required_elements_present",
                    "proper_nesting"
                ]
            },
            "markdown_table": {
                "required_structure": {
                    "headers": ["ID", "Name", "Status", "Priority"],
                    "min_rows": 1
                },
                "validation_rules": [
                    "proper_table_syntax",
                    "all_headers_present",
                    "consistent_columns"
                ]
            },
            "bullet_points": {
                "required_structure": {
                    "min_points": 3,
                    "max_points": 10,
                    "point_format": "- "
                },
                "validation_rules": [
                    "correct_bullet_format",
                    "within_point_limits",
                    "no_empty_points"
                ]
            },
            "numbered_list": {
                "required_structure": {
                    "min_items": 2,
                    "max_items": 8,
                    "number_format": "1. "
                },
                "validation_rules": [
                    "sequential_numbering",
                    "within_item_limits",
                    "proper_formatting"
                ]
            }
        }
    
    def validate_output_format(self, output, expected_format):
        """
        Validate if output matches expected format
        """
        validation_result = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "format_type": expected_format
        }
        
        if expected_format == "json":
            return self._validate_json(output, validation_result)
        elif expected_format == "xml":
            return self._validate_xml(output, validation_result)
        elif expected_format == "markdown_table":
            return self._validate_markdown_table(output, validation_result)
        elif expected_format == "bullet_points":
            return self._validate_bullet_points(output, validation_result)
        elif expected_format == "numbered_list":
            return self._validate_numbered_list(output, validation_result)
        else:
            validation_result["is_valid"] = False
            validation_result["errors"].append(f"Unknown format: {expected_format}")
            return validation_result
    
    def _validate_json(self, output, validation_result):
        """Validate JSON format"""
        try:
            parsed_json = json.loads(output)
            validation_result["parsed_data"] = parsed_json
            
            # Check required fields
            format_def = self.format_definitions["json"]
            required_fields = format_def["required_structure"]
            
            for field, field_type in required_fields.items():
                if field not in parsed_json:
                    validation_result["is_valid"] = False
                    validation_result["errors"].append(f"Missing required field: {field}")
                else:
                    # Basic type checking
                    if field_type == "string" and not isinstance(parsed_json[field], str):
                        validation_result["is_valid"] = False
                        validation_result["errors"].append(f"Field {field} must be string")
                    elif field_type == "object" and not isinstance(parsed_json[field], dict):
                        validation_result["is_valid"] = False
                        validation_result["errors"].append(f"Field {field} must be object")
        
        except json.JSONDecodeError as e:
            validation_result["is_valid"] = False
            validation_result["errors"].append(f"Invalid JSON: {str(e)}")
        
        return validation_result
    
    def _validate_xml(self, output, validation_result):
        """Validate XML format"""
        try:
            root = ET.fromstring(output)
            validation_result["parsed_data"] = root
            
            # Check required elements
            format_def = self.format_definitions["xml"]
            required_elements = format_def["required_structure"]["required_elements"]
            
            for element in required_elements:
                if root.find(element) is None:
                    validation_result["is_valid"] = False
                    validation_result["errors"].append(f"Missing required element: {element}")
        
        except ET.ParseError as e:
            validation_result["is_valid"] = False
            validation_result["errors"].append(f"Invalid XML: {str(e)}")
        
        return validation_result
    
    def _validate_markdown_table(self, output, validation_result):
        """Validate Markdown table format"""
        lines = output.strip().split('\n')
        
        if len(lines) < 2:
            validation_result["is_valid"] = False
            validation_result["errors"].append("Table must have at least header and separator rows")
            return validation_result
        
        # Check header line
        header_line = lines[0]
        if not header_line.startswith('|') or not header_line.endswith('|'):
            validation_result["is_valid"] = False
            validation_result["errors"].append("Header must start and end with |")
        
        # Check separator line
        if len(lines) > 1:
            separator_line = lines[1]
            if not re.match(r'^\|[\s\-\|]+\|$', separator_line):
                validation_result["is_valid"] = False
                validation_result["errors"].append("Invalid table separator format")
        
        # Check required headers
        format_def = self.format_definitions["markdown_table"]
        required_headers = format_def["required_structure"]["headers"]
        actual_headers = [h.strip() for h in header_line.split('|')[1:-1]]
        
        for header in required_headers:
            if header not in actual_headers:
                validation_result["warnings"].append(f"Missing expected header: {header}")
        
        # Check minimum rows
        data_rows = len(lines) - 2
        min_rows = format_def["required_structure"]["min_rows"]
        if data_rows < min_rows:
            validation_result["is_valid"] = False
            validation_result["errors"].append(f"Table must have at least {min_rows} data row(s)")
        
        return validation_result
    
    def _validate_bullet_points(self, output, validation_result):
        """Validate bullet points format"""
        lines = output.strip().split('\n')
        bullet_lines = [line.strip() for line in lines if line.strip().startswith('- ')]
        
        format_def = self.format_definitions["bullet_points"]
        min_points = format_def["required_structure"]["min_points"]
        max_points = format_def["required_structure"]["max_points"]
        
        if len(bullet_lines) < min_points:
            validation_result["is_valid"] = False
            validation_result["errors"].append(f"Must have at least {min_points} bullet points")
        
        if len(bullet_lines) > max_points:
            validation_result["is_valid"] = False
            validation_result["errors"].append(f"Cannot have more than {max_points} bullet points")
        
        # Check for empty points
        for i, point in enumerate(bullet_lines):
            if len(point) <= 2:  # Just "- "
                validation_result["is_valid"] = False
                validation_result["errors"].append(f"Bullet point {i+1} is empty")
        
        return validation_result
    
    def _validate_numbered_list(self, output, validation_result):
        """Validate numbered list format"""
        lines = output.strip().split('\n')
        numbered_lines = [line.strip() for line in lines if re.match(r'^\d+\.', line.strip())]
        
        format_def = self.format_definitions["numbered_list"]
        min_items = format_def["required_structure"]["min_items"]
        max_items = format_def["required_structure"]["max_items"]
        
        if len(numbered_lines) < min_items:
            validation_result["is_valid"] = False
            validation_result["errors"].append(f"Must have at least {min_items} numbered items")
        
        if len(numbered_lines) > max_items:
            validation_result["is_valid"] = False
            validation_result["errors"].append(f"Cannot have more than {max_items} numbered items")
        
        # Check sequential numbering
        for i, line in enumerate(numbered_lines):
            expected_num = i + 1
            if not line.startswith(f"{expected_num}."):
                validation_result["is_valid"] = False
                validation_result["errors"].append(f"Item {i+1} should start with '{expected_num}.'")
        
        return validation_result
    
    def create_format_controlled_prompt(self, user_query, output_format):
        """
        Create a prompt that enforces specific output format
        """
        format_instructions = {
            "json": """
RESPONSE FORMAT: JSON
Your response must be valid JSON with this exact structure:
{
    "status": "success/error",
    "message": "descriptive message",
    "data": {...},
    "timestamp": "YYYY-MM-DD HH:MM:SS"
}

DO NOT include any text before or after the JSON.
""",
            "xml": """
RESPONSE FORMAT: XML
Your response must be valid XML with this structure:
<response>
    <status>success/error</status>
    <message>descriptive message</message>
    <data>...</data>
</response>

DO NOT include any text before or after the XML.
""",
            "markdown_table": """
RESPONSE FORMAT: Markdown Table
Your response must be a valid Markdown table with these headers:
| ID | Name | Status | Priority |

Include at least one data row. Example:
| ID | Name | Status | Priority |
|----|-----|--------|----------|
| 1 | Task A | In Progress | High |

DO NOT include any text before or after the table.
""",
            "bullet_points": """
RESPONSE FORMAT: Bullet Points
Your response must be 3-10 bullet points using this format:
- Point 1
- Point 2
- Point 3

Each point should be informative and not empty.
DO NOT include any text before or after the bullet points.
""",
            "numbered_list": """
RESPONSE FORMAT: Numbered List
Your response must be 2-8 numbered items using this format:
1. First item
2. Second item
3. Third item

Each item should be informative and properly numbered.
DO NOT include any text before or after the numbered list.
"""
        }
        
        prompt = f"""{format_instructions.get(output_format, '')}

USER QUERY: {user_query}

RESPONSE:"""
        
        return prompt

# Test cases
test_cases = [
    {
        "name": "JSON Format - Valid",
        "query": "Create a response about project status",
        "format": "json"
    },
    {
        "name": "XML Format - Valid",
        "query": "Create a response about system health",
        "format": "xml"
    },
    {
        "name": "Markdown Table - Valid",
        "query": "List 3 tasks with their details",
        "format": "markdown_table"
    },
    {
        "name": "Bullet Points - Valid",
        "query": "Summarize the benefits of exercise",
        "format": "bullet_points"
    },
    {
        "name": "Numbered List - Valid",
        "query": "List steps to solve a problem",
        "format": "numbered_list"
    }
]

# Run output format guardrails demo
format_system = OutputFormatGuardrails()

print("=== Output Format Guardrails Demo ===\n")

for test_case in test_cases:
    print(f"🧪 Test: {test_case['name']}")
    print(f"📝 Query: {test_case['query']}")
    print(f"📋 Format: {test_case['format']}")
    
    # Generate response with format control
    prompt = format_system.create_format_controlled_prompt(test_case['query'], test_case['format'])
    
    try:
        response = get_completion(prompt)
        print(f"\n🤖 Raw Response:")
        print(response[:500] + "..." if len(response) > 500 else response)
        
        # Validate the format
        validation = format_system.validate_output_format(response, test_case['format'])
        
        print(f"\n📊 Format Validation:")
        if validation["is_valid"]:
            print("   ✅ Format is valid")
        else:
            print("   ❌ Format validation failed")
        
        for error in validation["errors"]:
            print(f"   {error}")
        
        for warning in validation["warnings"]:
            print(f"   ⚠️ {warning}")
        
    except Exception as e:
        print(f"\n❌ Error generating response: {e}")
    
    print("\n" + "="*60 + "\n")
