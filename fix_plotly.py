import os

filepath = 'c:/Users/hp/Desktop/polystorebench/polystorebench/polystorebench/dashboard/app.py'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Make sure Plotly charts don't use Streamlit's default theme override, which forces white text.
content = content.replace('use_container_width=True)', 'theme=None, use_container_width=True)')
content = content.replace('theme=None, theme=None,', 'theme=None,') # safeguard if run twice

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated app.py to enforce Plotly light theme.")
