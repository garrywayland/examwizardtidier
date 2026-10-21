#!/usr/bin/env python3
"""Builds index.html from src/v1.html (the original) and src/v2.html.

index.html is a small loader that holds both complete pages. It shows v1
unless the address ends in ?v=2 (or the visitor has chosen v2 with the
switch button), so the original URL keeps serving the original tool.

Edit src/v1.html or src/v2.html, then run:  python3 build.py
"""
import pathlib, sys

root = pathlib.Path(__file__).parent

def embed(name):
    text = (root / 'src' / name).read_text(encoding='utf-8')
    for bad in ('<\\/script', '<\\!--'):
        if bad in text:
            sys.exit(f'{name} already contains {bad!r}; the loader cannot embed it safely')
    # A literal </script> or <!-- would end / confuse the embedding <script> tag.
    return text.replace('</script', '<\\/script').replace('<!--', '<\\!--')

LOADER = r'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Exam Paper Builder</title>
<!-- Libraries shared by both versions, loaded once here: scripts that arrive
     through document.write can be blocked by browsers on slow connections. -->
<script src="https://cdnjs.cloudflare.com/ajax/libs/KaTeX/0.16.9/katex.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/html2pdf.js/0.9.3/html2pdf.bundle.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/jszip/3.10.1/jszip.min.js"></script>
</head>
<body>
<noscript>Exam Paper Builder needs JavaScript turned on.</noscript>
<!-- Both versions are kept whole below as inert text and one is written into
     the page at load. Edit src/v1.html / src/v2.html and run build.py rather
     than editing this file by hand. -->
<script type="text/plain" id="app-v1">@@V1@@</script>
<script type="text/plain" id="app-v2">@@V2@@</script>
<script>
(function () {
  var KEY = 'ewt-version';
  function stored() { try { return localStorage.getItem(KEY); } catch (e) { return null; } }
  function remember(v) { try { localStorage.setItem(KEY, v); } catch (e) {} }

  var q = new URLSearchParams(location.search).get('v');
  var version = (q === '1' || q === '2') ? q : (stored() === '2' ? '2' : '1');
  if (q === '1' || q === '2') remember(q);

  var html = document.getElementById('app-v' + version).textContent
    .replace(/<\\\/script/g, '<\/script')
    .replace(/<\\!--/g, '<!' + '--')
    // already loaded by this page's own <head> (see above)
    .replace(/<script[^>]*src="https:\/\/cdnjs\.cloudflare\.com[^>]*><\/script>\s*/g, '');

  var other = version === '1' ? '2' : '1';
  var chip =
    '<div id="ewt-version-chip" style="position:fixed;left:10px;bottom:10px;z-index:200;' +
    'font:12px/1.2 monospace;background:#1b1b1b;color:#f4f1ea;border-radius:6px;padding:6px 10px;' +
    'opacity:.85;display:flex;gap:8px;align-items:center;">' +
    '<span>v' + version + (version === '2' ? ' (new)' : '') + '</span>' +
    '<a href="#" id="ewt-switch" style="color:#f0c060;">Switch to v' + other + '</a></div>' +
    '<style>@media print{#ewt-version-chip{display:none!important}}</style>' +
    '<scr' + 'ipt>document.getElementById("ewt-switch").addEventListener("click",function(e){' +
    'e.preventDefault();try{localStorage.setItem("' + KEY + '","' + other + '")}catch(x){}' +
    'location.href=location.pathname+"?v=' + other + '";});<\/script>';

  var i = html.lastIndexOf('</body>');
  html = i === -1 ? html + chip : html.slice(0, i) + chip + html.slice(i);

  document.open();
  document.write(html);
  document.close();
})();
</script>
</body>
</html>
'''

out = LOADER.replace('@@V1@@', embed('v1.html')).replace('@@V2@@', embed('v2.html'))
(root / 'index.html').write_text(out, encoding='utf-8')
print('index.html written,', len(out) // 1024, 'KB')
