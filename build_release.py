#!/usr/bin/env python3
"""Build an offline-capable static document into the GitHub Pages /docs source."""
from pathlib import Path
import subprocess,sys,shutil
ROOT=Path(__file__).resolve().parent
subprocess.run([sys.executable,str(ROOT/'src/validate.py')],check=True)
subprocess.run([sys.executable,str(ROOT/'src/build.py')],check=True)
(ROOT/'docs').mkdir(exist_ok=True)
shutil.copyfile(ROOT/'src/index.html',ROOT/'docs/index.html')
(ROOT/'docs/.nojekyll').write_text('')
print('Built docs/index.html; this command does not publish anything.')
