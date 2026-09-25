p = r"D:\Nexa ai\My-Nexa\main.py"
lines = open(p, "r", encoding="utf-8").readlines()
out = []
for i, line in enumerate(lines):
    stripped = line.strip()
    if i > 0 and lines[i-1].strip().endswith(':'):
        prev_indent = lines[i-1][:len(lines[i-1]) - len(lines[i-1].lstrip())]
        curr_indent = line[:len(line) - len(line.lstrip())]
        if len(curr_indent) <= len(prev_indent) and stripped:
            out.append(prev_indent + '    ' + stripped + '\n')
            continue
    out.append(line)
open(p, "w", encoding="utf-8").writelines(out)
print("Syntax Block Indentation Repaired!")
