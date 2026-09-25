p = r"D:\Nexa ai\My-Nexa\main.py"
lines = open(p, "r", encoding="utf-8").readlines()
out = []
for i, line in enumerate(lines):
    if 'self.ui.set_state("LISTENING")' in line and i > 0 and lines[i-1].strip().endswith(':'):
        prev = lines[i-1]
        indent = prev[:len(prev) - len(prev.lstrip())] + '    '
        out.append(indent + line.strip() + '\n')
    else:
        out.append(line)
open(p, "w", encoding="utf-8").writelines(out)
print("Line 725 Indentation Fixed!")
