p = r"D:\Nexa ai\My-Nexa\main.py"
lines = open(p, "r", encoding="utf-8").readlines()
idx = 1306
if idx < len(lines):
    prev_indent = ''
    for l in reversed(lines[:idx]):
        if l.strip():
            prev_indent = l[:len(l)-len(l.lstrip())]
            break
    lines[idx] = prev_indent + lines[idx].lstrip()
    open(p, 'w', encoding='utf-8').writelines(lines)
    print('Line 1307 adjusted to previous indentation level.')
