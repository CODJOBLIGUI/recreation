from pathlib import Path
import re

p = Path('recreation-master/apps/catalogue/tasks.py')
txt = p.read_text(encoding='utf-8', errors='ignore')
pattern = r"(\n\s*if not text\.strip\(\):\n\s*_set_progress\(obj, \"failed\", 100, \"[^\"]*\"\)\n\s*return\n)"
match = re.search(pattern, txt)
payment_block = (
    "\n        if obj.paiement_requis and obj.statut != \"paid\":\n"
    "            _set_progress(obj, \"failed\", 100, \"Paiement requis non validé.\")\n"
    "            return\n"
)
if match and payment_block.strip() not in txt:
    txt = txt.replace(match.group(1), match.group(1) + payment_block)

for bad in ("aprÃ¨s", "aprÃ©s"):
    txt = txt.replace(bad, "après")

txt = txt.replace("apr\u00e8s extraction", "après extraction")

p.write_text(txt, encoding='utf-8')
print('OK')
