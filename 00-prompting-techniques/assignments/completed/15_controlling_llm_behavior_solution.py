"""
Assignment 15 — Controlling LLM Behavior Solution
Task: Create a workflow that controls and directs LLM behavior effectively
"""

import sys
from pathlib import Path
import re
from typing import Dict, List, Any

# allow importing from project root
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from helper import get_completion

class LLMBehaviorController:
    """
    Control and direct LLM behavior through various techniques
    """
    
    def __init__(self):
        self.behavior_modes = {
            "professional": {
                "tone": "formal, respectful, business-oriented",
                "style": "structured, concise, informative",
                "constraints": [
                    "no casual language",
                    "no personal opinions",
                    "no emotional expressions",
                    "focus on facts and data"
                ],
                "response_format": "business communication"
            },
            "educational": {
                "tone": "encouraging, patient, clear",
                "style": "step-by-step, explanatory, interactive",
                "constraints": [
                    "avoid jargon",
                    "provide examples",
                    "check understanding",
                    "encourage questions"
                ],
                "response_format": "learning module"
            },
            "creative": {
                "tone": "imaginative, expressive, innovative",
                "style": "descriptive, engaging, artistic",
                "constraints": [
                    "encourage creativity",
                    "use vivid language",
                    "explore possibilities",
                    "avoid rigid structure"
                ],
                "response_format": "creative content"
            },
            "technical": {
                "tone": "precise, accurate, objective",
                "style": "detailed, methodical, analytical",
                "constraints": [
                    "use technical terminology",
                    "provide specific details",
                    "include procedures",
                    "maintain accuracy"
                ],
                "response_format": "technical documentation"
            },
            "conversational": {
                "tone": "friendly, natural, approachable",
                "style": "dialogue-based, responsive, engaging",
                "constraints": [
                    "use natural language",
                    "ask follow-up questions",
                    "show empathy",
                    "maintain flow"
                ],
                "response_format": "conversation"
            }
        }
        
        self.control_techniques = {
            "role_setting": "Define specific role and persona for the AI",
            "constraint_setting": "Set clear boundaries and limitations",
            "output_formatting": "Specify exact response format requirements",
            "behavior_modeling": "Provide examples of desired behavior",
            "negative_constraints": "Specify what NOT to do",
            "context_setting": "Provide relevant context and background",
            "goal_orientation": "Clearly state the desired outcome",
            "audience_specification": "Define target audience for response"
        }
        
        self.behavior_metrics = {
            "tone_consistency": "How well the response matches intended tone",
            "style_adherence": "How well the response follows style guidelines",
            "constraint_compliance": "How well constraints are respected",
            "goal_achievement": "How well the response achieves intended goals",
            "audience_appropriateness": "How appropriate the response is for the audience"
        }
    
    def create_behavior_control_prompt(self, user_query: str, behavior_mode: str, 
                                     additional_constraints: List[str] = None) -> str:
        """
        Create a prompt with comprehensive behavior control
        """
        mode_config = self.behavior_modes.get(behavior_mode, self.behavior_modes["professional"])
        
        # Base behavior control
        prompt_parts = [
            f"BEHAVIOR MODE: {behavior_mode.upper()}",
            "",
            "ROLE AND PERSONA:",
            f"You are acting as a {behavior_mode} assistant.",
            f"TONE: {mode_config['tone']}",
            f"STYLE: {mode_config['style']}",
            "",
            "BEHAVIORAL CONSTRAINTS:"
        ]
        
        # Add mode-specific constraints
        for constraint in mode_config["constraints"]:
            prompt_parts.append(f"- {constraint}")
        
        # Add additional constraints if provided
        if additional_constraints:
            prompt_parts.extend(["ADDITIONAL CONSTRAINTS:"])
            for constraint in additional_constraints:
                prompt_parts.append(f"- {constraint}")
        
        # Add negative constraints
        prompt_parts.extend([
            "",
            "NEGATIVE CONSTRAINTS:",
            "- Do not deviate from the specified tone",
            "- Do not violate any behavioral constraints",
            "- Do not provide information outside your role",
            "- Do not switch behavior modes mid-response"
        ])
        
        # Add response format guidance
        prompt_parts.extend([
            "",
            f"RESPONSE FORMAT: {mode_config['response_format']}",
            "",
            "USER QUERY:",
            user_query,
            "",
            "RESPONSE:"
        ])
        
        return "\n".join(prompt_parts)
    
    def analyze_response_behavior(self, response: str, intended_mode: str) -> Dict[str, Any]:
        """
        Analyze if response matches intended behavior
        """
        mode_config = self.behavior_modes.get(intended_mode, self.behavior_modes["professional"])
        
        analysis = {
            "intended_mode": intended_mode,
            "compliance_score": 0,
            "tone_analysis": {},
            "style_analysis": {},
            "constraint_compliance": {},
            "recommendations": []
        }
        
        # Tone analysis
        tone_indicators = {
            "professional": ["please", "thank you", "regarding", "furthermore", "additionally"],
            "educational": ["let's", "consider", "notice", "remember", "important"],
            "creative": ["imagine", "envision", "picture", "discover", "explore"],
            "technical": ["specifically", "precisely", "according", "procedure", "method"],
            "conversational": ["hey", "what's", "how about", "sounds", "feel"]
        }
        
        response_lower = response.lower()
        tone_score = 0
        tone_matches = []
        
        for indicator in tone_indicators.get(intended_mode, []):
            if indicator in response_lower:
                tone_score += 1
                tone_matches.append(indicator)
        
        analysis["tone_analysis"] = {
            "score": tone_score,
            "matches": tone_matches,
            "compliance": "GOOD" if tone_score >= 2 else "NEEDS_IMPROVEMENT"
        }
        
        # Style analysis
        style_metrics = {
            "professional": {"formality": "high", "structure": "organized", "length": "medium"},
            "educational": {"clarity": "high", "examples": "present", "interactivity": "medium"},
            "creative": {"descriptiveness": "high", "imagination": "high", "structure": "flexible"},
            "technical": {"precision": "high", "detail": "high", "accuracy": "critical"},
            "conversational": ["naturalness", "flow", "engagement"]
        }
        
        # Simplified style analysis
        style_score = 0
        if intended_mode == "professional":
            if any(word in response_lower for word in ["furthermore", "additionally", "regarding"]):
                style_score += 1
            if len(response.split('.')) > 3:  # Multiple sentences
                style_score += 1
        elif intended_mode == "educational":
            if "example" in response_lower or "for instance" in response_lower:
                style_score += 1
            if any(word in response_lower for word in ["understand", "learn", "consider"]):
                style_score += 1
        elif intended_mode == "creative":
            if any(word in response_lower for word in ["imagine", "envision", "picture"]):
                style_score += 1
            if len(response) > 200:  # Descriptive length
                style_score += 1
        
        analysis["style_analysis"] = {
            "score": style_score,
            "compliance": "GOOD" if style_score >= 1 else "NEEDS_IMPROVEMENT"
        }
        
        # Constraint compliance
        constraint_compliance = {}
        for constraint in mode_config["constraints"]:
            if "no casual" in constraint and any(word in response_lower for word in ["hey", "what's up", "cool"]):
                constraint_compliance[constraint] = "VIOLATED"
            elif "no personal" in constraint and "i think" in response_lower:
                constraint_compliance[constraint] = "VIOLATED"
            else:
                constraint_compliance[constraint] = "COMPLIED"
        
        analysis["constraint_compliance"] = constraint_compliance
        
        # Calculate overall compliance score
        total_checks = 3  # tone, style, constraints
        passed_checks = sum([
            1 if analysis["tone_analysis"]["compliance"] == "GOOD" else 0,
            1 if analysis["style_analysis"]["compliance"] == "GOOD" else 0,
            1 if all(status == "COMPLIED" for status in constraint_compliance.values()) else 0
        ])
        
        analysis["compliance_score"] = (passed_checks / total_checks) * 100
        
        # Generate recommendations
        if analysis["compliance_score"] < 80:
            analysis["recommendations"] = [
                "Strengthen role definition in prompt",
                "Add more specific constraints",
                "Provide examples of desired behavior",
                "Use negative constraints more effectively"
            ]
        
        return analysis
    
    def demonstrate_behavior_control(self, user_query: str) -> Dict[str, Any]:
        """
        Demonstrate different behavior modes for the same query
        """
        demonstration = {
            "query": user_query,
            "modes_tested": [],
            "comparison_analysis": {}
        }
        
        # Test each behavior mode
        for mode_name in self.behavior_modes.keys():
            try:
                # Create mode-specific prompt
                prompt = self.create_behavior_control_prompt(user_query, mode_name)
                
                # Generate response
                response = get_completion(prompt)
                
                # Analyze response
                analysis = self.analyze_response_behavior(response, mode_name)
                
                mode_result = {
                    "mode": mode_name,
                    "prompt": prompt,
                    "response": response,
                    "analysis": analysis
                }
                
                demonstration["modes_tested"].append(mode_result)
                
            except Exception as e:
                demonstration["modes_tested"].append({
                    "mode": mode_name,
                    "error": str(e),
                    "analysis": {"compliance_score": 0}
                })
        
        # Compare results
        if demonstration["modes_tested"]:
            scores = {result["mode"]: result["analysis"].get("compliance_score", 0) 
                     for result in demonstration["modes_tested"] if "analysis" in result}
            
            demonstration["comparison_analysis"] = {
                "best_mode": max(scores, key=scores.get) if scores else None,
                "worst_mode": min(scores, key=scores.get) if scores else None,
                "average_score": sum(scores.values()) / len(scores) if scores else 0,
                "score_range": f"{min(scores.values())}-{max(scores.values())}" if scores else "N/A"
            }
        
        return demonstration
    
    def create_advanced_control_prompt(self, user_query: str, 
                                    control_config: Dict[str, Any]) -> str:
        """
        Create advanced behavior control prompt with multiple techniques
        """
        prompt_parts = [
            "ADVANCED BEHAVIOR CONTROL SYSTEM",
            "",
            "PRIMARY DIRECTIVE:",
            control_config.get("primary_directive", "Provide helpful and accurate information"),
            "",
            "ROLE DEFINITION:",
            f"You are a {control_config.get('role', 'helpful assistant')}.",
            f"Your expertise level: {control_config.get('expertise_level', 'knowledgeable')}.",
            f"Your personality: {control_config.get('personality', 'professional and friendly')}.",
            "",
            "BEHAVIORAL FRAMEWORK:",
        ]
        
        # Add behavioral framework
        framework = control_config.get("behavioral_framework", {})
        for aspect, guidance in framework.items():
            prompt_parts.append(f"- {aspect.upper()}: {guidance}")
        
        # Add control techniques
        prompt_parts.extend([
            "",
            "CONTROL TECHNIQUES APPLIED:",
        ])
        
        techniques = control_config.get("control_techniques", [])
        for technique in techniques:
            if technique == "role_setting":
                prompt_parts.append("- Role-based interaction enforced")
            elif technique == "constraint_setting":
                prompt_parts.append("- Behavioral constraints active")
            elif technique == "output_formatting":
                prompt_parts.append("- Output format requirements enforced")
            elif technique == "negative_constraints":
                prompt_parts.append("- Negative constraints applied")
        
        # Add specific constraints
        constraints = control_config.get("constraints", [])
        if constraints:
            prompt_parts.extend([
                "",
                "SPECIFIC CONSTRAINTS:"
            ])
            for constraint in constraints:
                prompt_parts.append(f"- {constraint}")
        
        # Add audience specification
        audience = control_config.get("audience")
        if audience:
            prompt_parts.extend([
                "",
                f"TARGET AUDIENCE: {audience}",
                f"Adapt language and complexity for: {audience}"
            ])
        
        # Add goal specification
        goal = control_config.get("goal")
        if goal:
            prompt_parts.extend([
                "",
                f"PRIMARY GOAL: {goal}",
                "Ensure response directly addresses this goal."
            ])
        
        prompt_parts.extend([
            "",
            "USER QUERY:",
            user_query,
            "",
            "RESPONSE:"
        ])
        
        return "\n".join(prompt_parts)

# Test cases
test_cases = [
    {
        "name": "Basic Query - Multiple Modes",
        "query": "Explain the importance of teamwork in business"
    },
    {
        "name": "Technical Query - Mode Comparison",
        "query": "How does machine learning work?"
    },
    {
        "name": "Creative Query - Behavior Control",
        "query": "Write about a sunset"
    },
    {
        "name": "Educational Query - Advanced Control",
        "query": "Teach me about photosynthesis"
    }
]

# Run LLM behavior control demo
behavior_controller = LLMBehaviorController()

print("=== LLM Behavior Control Demo ===\n")

for test_case in test_cases:
    print(f"🧪 Test: {test_case['name']}")
    print(f"📝 Query: {test_case['query']}")
    
    # Demonstrate different behavior modes
    demonstration = behavior_controller.demonstrate_behavior_control(test_case['query'])
    
    print(f"\n📊 Behavior Mode Comparison:")
    comparison = demonstration["comparison_analysis"]
    print(f"   Best Mode: {comparison.get('best_mode', 'N/A')}")
    print(f"   Average Score: {comparison.get('average_score', 0):.1f}%")
    print(f"   Score Range: {comparison.get('score_range', 'N/A')}")
    
    print(f"\n📋 Mode Results:")
    for result in demonstration["modes_tested"]:
        if "error" in result:
            print(f"   ❌ {result['mode']}: Error - {result['error']}")
        else:
            analysis = result["analysis"]
            print(f"   {'✅' if analysis['compliance_score'] >= 80 else '⚠️'} {result['mode']}: {analysis['compliance_score']:.0f}%")
            print(f"      Tone: {analysis['tone_analysis']['compliance']}")
            print(f"      Style: {analysis['style_analysis']['compliance']}")
            print(f"      Constraints: {sum(1 for v in analysis['constraint_compliance'].values() if v == 'COMPLIED')}/{len(analysis['constraint_compliance'])} complied")
            
            # Show sample response
            response_sample = result["response"][:150] + "..." if len(result["response"]) > 150 else result["response"]
            print(f"      Sample: {response_sample}")
    
    print("\n" + "="*60 + "\n")

# Advanced control demonstration
print("🔧 Advanced Behavior Control Demo\n")

advanced_config = {
    "primary_directive": "Provide comprehensive yet accessible explanation",
    "role": "expert educator",
    "expertise_level": "advanced",
    "personality": "patient and encouraging",
    "behavioral_framework": {
        "communication": "clear and structured",
        "interaction": "supportive and engaging",
        "content": "accurate and well-organized"
    },
    "control_techniques": ["role_setting", "constraint_setting", "output_formatting"],
    "constraints": [
        "Use analogies to explain complex concepts",
        "Include real-world examples",
        "Check for understanding",
        "Avoid overwhelming technical details"
    ],
    "audience": "intelligent beginners",
    "goal": "Ensure deep understanding through clear explanation"
}

advanced_query = "Explain quantum computing in simple terms"
advanced_prompt = behavior_controller.create_advanced_control_prompt(advanced_query, advanced_config)

print(f"📝 Advanced Query: {advanced_query}")
print(f"\n🔧 Generated Advanced Prompt:")
print(advanced_prompt[:800] + "..." if len(advanced_prompt) > 800 else advanced_prompt)

try:
    advanced_response = get_completion(advanced_prompt)
    print(f"\n🤖 Advanced Response:")
    print(advanced_response[:400] + "..." if len(advanced_response) > 400 else advanced_response)
    
    # Analyze advanced response
    analysis = behavior_controller.analyze_response_behavior(advanced_response, "educational")
    print(f"\n📊 Advanced Analysis: {analysis['compliance_score']:.0f}% compliance")
    
except Exception as e:
    print(f"\n❌ Error: {e}")

print("\n" + "="*60)
print(f"\n📚 Behavior Control Summary:")
print(f"Available Modes: {list(behavior_controller.behavior_modes.keys())}")
print(f"Control Techniques: {list(behavior_controller.control_techniques.keys())}")
print(f"Behavior Metrics: {list(behavior_controller.behavior_metrics.keys())}")
