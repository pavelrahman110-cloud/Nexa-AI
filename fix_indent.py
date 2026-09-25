p = r"D:\Nexa ai\My-Nexa\main.py"
lines = open(p, "r", encoding="utf-8").readlines()
out = []
for line in lines:
    if "self.ui.on_file_uploaded" in line:
        ref = "        "
        for prev in reversed(out):
            if "self.ui.on_text_command" in prev:
                ref = prev[:len(prev) - len(prev.lstrip())]
                break
        out.append(ref + "self.ui.on_file_uploaded = self.handle_uploaded_file\n")
    else:
        out.append(line)
open(p, "w", encoding="utf-8").writelines(out)
print("Indentation successfully fixed!")
