#!/usr/bin/env python3

# Read tasks.md
with open('.kiro/specs/govt-scheme-rag/tasks.md', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace all occurrences
content = content.replace(
    'Hindi, English, Tamil, Telugu, Bengali, Marathi, Gujarati, Kannada, Malayalam, Punjabi',
    'English (default), Hindi, Tamil'
)

content = content.replace(
    '10 language tiles',
    '3 language tiles'
)

content = content.replace(
    'with 10 language',
    'with 3 language'
)

# Write back
with open('.kiro/specs/govt-scheme-rag/tasks.md', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Fixed all language references in tasks.md")
print("   Changed: 10 languages → 3 languages (English, Hindi, Tamil)")
