"""
Assignment 09 — Prompt Reuse and Versioning Solution
Task: Create a reusable prompt template with versioning
"""

import sys
from pathlib import Path

# allow importing from project root
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from helper import get_completion

# Prompt template v1.0
def create_email_prompt(recipient, purpose, tone="professional"):
    """
    Create a prompt for generating emails with customizable parameters
    Version: 1.0
    """
    template = f"""
# EMAIL GENERATION PROMPT v1.0

# PARAMETERS
- Recipient: {recipient}
- Purpose: {purpose}
- Tone: {tone}

# TASK
Generate a professional email for the specified purpose and recipient.

# REQUIREMENTS
- Length: 150-200 words
- Clear subject line
- Appropriate greeting and closing
- Call to action if needed

# TONE GUIDELINES
{get_tone_guidelines(tone)}

# OUTPUT FORMAT
Subject: [Clear, concise subject line]

[Email body with proper formatting]

[Professional closing]
"""
    return template

def get_tone_guidelines(tone):
    guidelines = {
        "professional": "Formal language, proper business etiquette, clear and direct communication",
        "friendly": "Warm and approachable, slightly less formal but still professional",
        "urgent": "Direct and action-oriented, clear timeline, sense of importance",
        "apologetic": "Sincere and empathetic, takes responsibility, offers solutions"
    }
    return guidelines.get(tone, guidelines["professional"])

# Example usage
prompt = create_email_prompt(
    recipient="Project Manager",
    purpose="Request deadline extension for project deliverable",
    tone="professional"
)

response = get_completion(prompt)

print("Generated Prompt:")
print("-" * 50)
print(prompt)

print("\nResponse:")
print("-" * 50)
print(response)
