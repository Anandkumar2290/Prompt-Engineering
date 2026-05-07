"""
Assignment 01 — Zero-shot Prompting Solution
Task: Rewrite the following paragraph to be more concise and professional
"""

import sys
from pathlib import Path

# allow importing from project root
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from helper import get_completion

prompt = """
Rewrite the following paragraph to be more concise and professional:

The thing is, we need to like, definitely get this project done as soon as possible because it's really important and we have a deadline coming up pretty soon and everyone is counting on us to deliver good results that will make the stakeholders happy with our performance.
"""

response = get_completion(prompt)

print("Prompt:")
print("-" * 50)
print(prompt)

print("\nResponse:")
print("-" * 50)
print(response)
