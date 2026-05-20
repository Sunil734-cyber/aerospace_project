#!/usr/bin/env python3
"""Fix corrupted emoji characters in app.py"""

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace the corrupted mode list
content = content.replace(
    '["🧮 Calculate Dimensions", "� 3D Visualization", "�🎯 Quick Optimizer"',
    '["🧮 Calculate Dimensions", "🎨 3D Visualization", "🎯 Quick Optimizer"'
)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('✅ Fixed corrupted emojis')
