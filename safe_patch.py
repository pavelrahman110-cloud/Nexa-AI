p = r"D:\Nexa ai\My-Nexa\main.py"
txt = open(p, 'r', encoding='utf-8').read()
target = 'self.ui.on_text_command = self._on_text_command'
if target in txt and 'self.ui.on_file_uploaded' not in txt:
    idx = txt.find(target)
    line_start = txt.rfind('\n', 0, idx) + 1
    indent = txt[line_start:idx]
    injection = f"{indent}self.ui.on_file_uploaded = self.handle_uploaded_file\n"
    txt = txt[:line_start] + injection + txt[line_start:]
    open(p, 'w', encoding='utf-8').write(txt)
    print('UI Hook safely injected!')
else:
    print('Already hooked or target not matched')
