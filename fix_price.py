with open('main.py', 'r') as f:
    content = f.read()

# Replace $99/mo with $299/mo
content = content.replace('Deploy Your Swarm → $99/mo', 'Deploy Your Swarm → $299/mo')

with open('main.py', 'w') as f:
    f.write(content)

print("✅ Fixed price to $299/mo!")
