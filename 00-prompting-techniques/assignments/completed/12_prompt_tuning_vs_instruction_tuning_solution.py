"""
Assignment 12 — Prompt Tuning vs Instruction Tuning Solution
Task: Demonstrate the difference between prompt tuning and instruction tuning
"""

import sys
from pathlib import Path

# allow importing from project root
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from helper import get_completion

# Example 1: Instruction Tuning Approach (explicit instructions)
instruction_tuning_prompt = """
You are a professional business analyst. Your task is to analyze the following business scenario and provide recommendations.

Instructions:
1. Identify the main problem
2. Analyze the root causes
3. Provide 3 specific recommendations
4. Include potential risks for each recommendation
5. Format your response as a structured report

Business Scenario:
"A retail company has seen a 30% drop in foot traffic over the past 6 months. 
Online sales have increased by 15%, but overall revenue is down 10%. 
Customer satisfaction scores have also declined from 4.2 to 3.8 out of 5."

Please provide your analysis following the instructions above.
"""

# Example 2: Prompt Tuning Approach (optimized prompt design)
prompt_tuning_prompt = """
CONTEXT: You're an expert retail business analyst with 15+ years experience.
TASK: Analyze declining retail performance and provide actionable recommendations.
FORMAT: Structured business report with clear sections.

SCENARIO: 
- Foot traffic: -30% (6 months)
- Online sales: +15%  
- Overall revenue: -10%
- Customer satisfaction: 4.2 → 3.8/5

REQUIREMENTS:
• Problem identification with supporting data
• Root cause analysis (minimum 3 factors)
• 3 prioritized recommendations with implementation timeline
• Risk assessment for each recommendation
• Expected outcomes and success metrics

STYLE: Professional, data-driven, concise but comprehensive
"""

# Example 3: Comparison Demonstration
comparison_prompt = """
Compare these two approaches for the same task:

APPROACH A (Instruction-based):
"Summarize this article and give me the main points."

APPROACH B (Prompt-tuned):
"As a research assistant, create a concise executive summary of this article, highlighting: 1) Key findings, 2) Implications, 3) Action items. Limit to 150 words."

Article: "Recent studies show that remote work has increased productivity by 22% on average, but employee burnout rates have also risen by 15%. Companies implementing hybrid models report the best outcomes, with 18% productivity gains and only 5% increase in burnout."

Please demonstrate both approaches and explain why Approach B typically yields better results.
"""

print("=== Instruction Tuning Approach ===")
response1 = get_completion(instruction_tuning_prompt)
print(response1)

print("\n=== Prompt Tuning Approach ===")
response2 = get_completion(prompt_tuning_prompt)
print(response2)

print("\n=== Comparison Demonstration ===")
response3 = get_completion(comparison_prompt)
print(response3)

print("\n=== Key Differences Summary ===")
print("Instruction Tuning:")
print("- Focuses on explicit step-by-step instructions")
print("- More verbose and detailed")
print("- Less dependent on prompt engineering")

print("\nPrompt Tuning:")
print("- Optimizes prompt structure and wording")
print("- More concise and targeted")
print("- Requires understanding of model behavior")
