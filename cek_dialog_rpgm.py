import zipfile
import json
import re

def is_dialog_string(line):
    if not isinstance(line, str): return False
    s = line.strip()
    # Harus lebih dari 8 karakter ATAU punya minimal 3 kata
    if len(s) < 8 and len(s.split()) < 3:
        return False
    # Minimal ada tanda baca umum dialog
    if not re.search(r'[.?!,"”“:;。？！、]', s):
        return False
    # Wajib ada huruf
    if not re.search(r'[a-zA-Z]', s):
        return False
    # Hindari kode/tag murni
    if re.match(r'^<[^>]+>$', s): return False
    return True

# Key umum dialog RPGM
dialog_keys = {"text", "message", "desc", "lines", "messages"}
# Event code yang biasanya berisi dialog (untuk RPGMV/MZ event)
dialog_codes = {101, 102, 401, 405}

def scan_zip_for_dialogs(zip_path):
    with zipfile.ZipFile(zip_path, 'r') as zipf:
        dialog_files = []
        for fname in zipf.namelist():
            if not fname.lower().endswith('.json'):
                continue
            try:
                content = zipf.read(fname).decode('utf-8')
                data = json.loads(content)
                found = False
                def recursive_check(obj):
                    nonlocal found
                    if found: return
                    # Dialog key klasik
                    if isinstance(obj, dict):
                        for k, v in obj.items():
                            # 1. Key dialog langsung (text, message, lines, dsb)
                            if k.lower() in dialog_keys:
                                if isinstance(v, list):
                                    if any(is_dialog_string(str(s)) for s in v):
                                        found = True
                                        return
                                elif isinstance(v, str):
                                    if is_dialog_string(v):
                                        found = True
                                        return
                            # 2. RPGM event: commandList/code/parameters
                            if k == "code" and "parameters" in obj:
                                if obj["code"] in dialog_codes:
                                    params = obj["parameters"]
                                    if isinstance(params, list) and any(is_dialog_string(str(p)) for p in params):
                                        found = True
                                        return
                        for v in obj.values():
                            recursive_check(v)
                    elif isinstance(obj, list):
                        for item in obj:
                            recursive_check(item)
                recursive_check(data)
                if found:
                    dialog_files.append(fname)
            except Exception:
                continue
        return dialog_files

# --- Ganti path sesuai lokasi ZIP-mu
zipname = "/storage/emulated/0/Download/Game.zip"

if __name__ == "__main__":
    hasil = scan_zip_for_dialogs(zipname)
    print("File yang mengandung dialog RPGM:")
    for f in hasil:
        print(f)