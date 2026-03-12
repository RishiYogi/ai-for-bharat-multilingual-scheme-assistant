#!/usr/bin/env python3
import re

# Read the design.md file
with open('.kiro/specs/govt-scheme-rag/design.md', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace all language references
replacements = [
    # 10 language tiles -> 3 language tiles
    (r'Display 10 language tiles', 'Display 3 language tiles'),
    
    # Full language list -> 3 languages
    (r'Hindi, English, Tamil, Telugu, Bengali, Marathi, Gujarati, Kannada, Malayalam, Punjabi', 
     'English (default), Hindi, Tamil'),
    
    # Multilingual UI translations for 10 languages -> 3 languages
    (r'Multilingual UI translations for all 10 languages', 
     'Multilingual UI translations for all 3 languages (English, Hindi, Tamil)'),
    
    # Test multilingual UI in all 10 languages -> 3 languages
    (r'Test multilingual UI in all 10 languages', 
     'Test multilingual UI in all 3 languages (English, Hindi, Tamil)'),
]

for old, new in replacements:
    content = re.sub(old, new, content)

# Write back
with open('.kiro/specs/govt-scheme-rag/design.md', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Updated design.md - changed from 10 languages to 3 languages (English, Hindi, Tamil)")

# Now update tasks.md
with open('.kiro/specs/govt-scheme-rag/tasks.md', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace language references in tasks.md
replacements_tasks = [
    # 10 language tiles -> 3 language tiles
    (r'10 language tiles', '3 language tiles'),
    (r'10 languages', '3 languages (English, Hindi, Tamil)'),
    
    # Test multilingual UI
    (r'Test multilingual UI in all 10 languages', 
     'Test multilingual UI in all 3 languages (English, Hindi, Tamil)'),
     
    # Multilingual translations
    (r'Multilingual UI translations for all 10 languages',
     'Multilingual UI translations for all 3 languages (English, Hindi, Tamil)'),
]

for old, new in replacements_tasks:
    content = re.sub(old, new, content)

# Write back
with open('.kiro/specs/govt-scheme-rag/tasks.md', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Updated tasks.md - changed from 10 languages to 3 languages (English, Hindi, Tamil)")

print("\n✅ All files updated successfully!")
print("Languages: English (default), Hindi, Tamil")
