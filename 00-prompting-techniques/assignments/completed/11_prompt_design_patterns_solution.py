"""
Assignment 11 — Prompt Design Patterns Solution
Task: Implement common prompt design patterns
"""

import sys
from pathlib import Path

# allow importing from project root
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from helper import get_completion

# Pattern 1: Chain of Thought with Self-Consistency
cot_self_consistency_prompt = """
Solve this math problem and show your reasoning, then provide the final answer:

Problem: A bakery sells 120 cupcakes per day. Each cupcake costs $3.50. 
If the bakery operates 6 days a week and has monthly expenses of $8,000,
what is their monthly profit?

Think step by step:
1. Calculate daily revenue
2. Calculate weekly revenue  
3. Calculate monthly revenue
4. Subtract monthly expenses
5. State the final profit

Final Answer:
"""

# Pattern 2: Template-Based Generation
template_prompt = """
Fill in this template for a project status report:

Project: [Project Name]
Status: [On Track/At Risk/Delayed]
Progress: [X]% complete
Key Achievements: 
- [Achievement 1]
- [Achievement 2]  
- [Achievement 3]
Challenges:
- [Challenge 1]
- [Challenge 2]
Next Steps:
- [Next Step 1]
- [Next Step 2]

Now fill this template for:
Project: E-commerce Website Redesign
Status: On Track
Progress: 75% complete
"""

# Pattern 3: Decomposition Pattern
decomposition_prompt = """
Break down this complex task into smaller, manageable steps:

Task: "Plan and execute a company-wide training program on AI ethics"

Please decompose this into:
1. Planning Phase (3-4 steps)
2. Development Phase (3-4 steps)  
3. Implementation Phase (3-4 steps)
4. Follow-up Phase (2-3 steps)

Each step should be specific and actionable.
"""

# Pattern 4: Reverse Pattern (Generate then Analyze)
reverse_pattern_prompt = """
First, generate a marketing slogan for a new eco-friendly water bottle.
Then, analyze why that slogan would be effective.

Step 1: Generate the slogan
Step 2: Analyze its effectiveness (target audience, emotional appeal, memorability)
"""

print("=== Pattern 1: Chain of Thought with Self-Consistency ===")
response1 = get_completion(cot_self_consistency_prompt)
print(response1)

print("\n=== Pattern 2: Template-Based Generation ===")
response2 = get_completion(template_prompt)
print(response2)

print("\n=== Pattern 3: Decomposition Pattern ===")
response3 = get_completion(decomposition_prompt)
print(response3)

print("\n=== Pattern 4: Reverse Pattern ===")
response4 = get_completion(reverse_pattern_prompt)
print(response4)
