with open('main.py', 'r') as f:
    content = f.read()

# Fix the wallet nav item
old = '<div class="nav-icon">💼</div>WALLET</div>'
new = '<div class="nav-item"><div class="nav-icon">💼</div>WALLET</div>'

content = content.replace(old, new)

with open('main.py', 'w') as f:
    f.write(content)

print("✅ Fixed wallet nav item!")
