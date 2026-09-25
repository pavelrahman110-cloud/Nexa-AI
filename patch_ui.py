import os, glob
base = r'D:\Nexa ai\My-Nexa'
files = glob.glob(os.path.join(base, 'ui*.py')) + glob.glob(os.path.join(base, 'ui', '*.py'))
target = None
for f in files:
    txt = open(f, 'r', encoding='utf-8', errors='ignore').read()
    if 'current_file' in txt:
        target = f
        break
if target:
    t = open(target, 'r', encoding='utf-8').read()
    if 'on_file_uploaded' not in t:
        t = t.replace('self.current_file =', 'if hasattr(self, "on_file_uploaded") and callable(self.on_file_uploaded):\n            self.on_file_uploaded(getattr(self, "current_file", None))\n        self.current_file =')
        open(target, 'w', encoding='utf-8').write(t)
        print('Successfully hooked into:', os.path.basename(target))
    else:
        print('Already hooked in:', os.path.basename(target))
else:
    print('UI file with current_file not found')
