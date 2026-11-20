"""Ekstrak blok CSS dari app.py ke file .css untuk diuji sloplint."""
import pathlib
import re
import sys
import types

src = pathlib.Path("app.py").read_text(encoding="utf-8")
head = src.split("# Pemuatan model")[0]

stub = types.ModuleType("streamlit")
sys.modules["streamlit"] = stub
ns = {"__file__": str(pathlib.Path("app.py").resolve())}
exec(compile(head, "app.py", "exec"), ns)

out = pathlib.Path("shots/_tmp")
out.mkdir(parents=True, exist_ok=True)
for mode in ("dark", "light"):
    css = ns["css"](mode)
    # Hallmark stamp harus jadi baris pertama non-kosong CSS
    (out / f"app_{mode}.css").write_text(css, encoding="utf-8")
    print("wrote", out / f"app_{mode}.css", len(css), "chars")
