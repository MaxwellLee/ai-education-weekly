#!/usr/bin/env python3
"""Build the public Pages site, preserving source image bytes."""
from pathlib import Path
import subprocess,sys,shutil,base64,mimetypes
ROOT=Path(__file__).resolve().parent
subprocess.run([sys.executable,str(ROOT/'src/validate.py')],check=True)
subprocess.run([sys.executable,str(ROOT/'src/build.py')],check=True)
document=(ROOT/'src/index.html').read_text(encoding='utf-8')
# Keep the public HTML small; the offline builder still embeds images.
for image in (ROOT/'src/assets').rglob('*'):
 if image.is_file():
  uri='data:'+(mimetypes.guess_type(image)[0] or 'image/jpeg')+';base64,'+base64.b64encode(image.read_bytes()).decode()
  document=document.replace(uri,image.relative_to(ROOT/'src').as_posix())
(ROOT/'src/index.html').write_text(document,encoding='utf-8')
(ROOT/'docs').mkdir(exist_ok=True)
shutil.copytree(ROOT/'src/assets',ROOT/'docs/assets',dirs_exist_ok=True)
shutil.copyfile(ROOT/'src/index.html',ROOT/'docs/index.html')
(ROOT/'docs/.nojekyll').write_text('')
print('Built public docs/index.html and image assets.')
