import os
import sys

print("Python path:", sys.path)
print("Current dir:", os.getcwd())
for root, dirs, files in os.walk('/home/inventree'):
    for f in files:
        if f in ['manage.py', 'settings.py']:
            print("Found:", os.path.join(root, f))
