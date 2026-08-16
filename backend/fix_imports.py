import os
import re

app_dir = r"D:\rag-in-goa\backend\app"
modules = ['api', 'chunking', 'generation', 'guardrails', 'harness', 'indexing', 'observability', 'retrieval', 'stt']
pattern = re.compile(r'^(from|import)\s+(' + '|'.join(modules) + r')\b', re.MULTILINE)

for root, _, files in os.walk(app_dir):
    for f in files:
        if f.endswith('.py'):
            path = os.path.join(root, f)
            with open(path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            new_content = pattern.sub(r'\1 app.\2', content)
            
            # Also fix from backend.app.indexing...
            new_content = new_content.replace('from backend.app.', 'from app.')
            
            if new_content != content:
                with open(path, 'w', encoding='utf-8') as file:
                    file.write(new_content)
                print(f"Updated {path}")
