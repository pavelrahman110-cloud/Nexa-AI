p = r"D:\Nexa ai\My-Nexa\main.py"
lines = open(p, "r", encoding="utf-8").readlines()
for i in range(1300, min(1312, len(lines))):
    l = lines[i]
    if any(k in l for k in ["_mode  =", "_query =", "_label =", "self.ui.show_content"]):
        lines[i] = "                        " + l.strip() + "\n"
open(p, "w", encoding="utf-8").writelines(lines)
print("Lines 1306-1309 Indentation Fixed!")
