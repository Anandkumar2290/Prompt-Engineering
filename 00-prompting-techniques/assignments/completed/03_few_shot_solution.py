"""
Assignment 03 — Few-shot Prompting Solution
Task: Classify customer feedback as positive, negative, or neutral using multiple examples
"""

import sys
from pathlib import Path

# allow importing from project root
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from helper import get_completion

prompt = """
Classify the following customer feedback as Positive, Negative, or Neutral.

Examples:
Input: "The product exceeded my expectations and works perfectly!"
Output: Positive

Input: "The delivery was late and the package was damaged."
Output: Negative

Input: "The item arrived on time and was as described."
Output: Neutral

Now classify this feedback:
Input: "I'm really impressed with the customer service, they resolved my issue quickly."
Output:
"""

response = get_completion(prompt)

print("Prompt:")
print("-" * 50)
print(prompt)

print("\nResponse:")
print("-" * 50)
print(response)
