p = r"D:\Nexa ai\My-Nexa\main.py"
lines = open(p, "r", encoding="utf-8").readlines()
out = []
i = 0
while i < len(lines):
    l = lines[i]
    if 'if "API key not valid" in err_str' in l:
        out.append('                if "API key not valid" in err_str or "1007" in err_str:\n')
        out.append('                    self.ui.write_log("ERR: API key invalid - please re-enter your key.")\n')
        out.append('                    self.ui.set_state("SLEEPING")\n')
        out.append('                    self.ui.prompt_reconfig()\n')
        out.append('                    while not self.ui._win._ready:\n')
        out.append('                        await asyncio.sleep(1)\n')
        out.append('                    print("[JARVIS] New API key saved - reconnecting...")\n')
        out.append('                    _conn_backoff = 3\n')
        out.append('                    continue\n')
        while i < len(lines) and not ('is_net_err =' in lines[i] or '# Network' in lines[i]):
            i += 1
        continue
    out.append(l)
    i += 1
open(p, "w", encoding="utf-8").writelines(out)
print("API block indentation strictly repaired!")
