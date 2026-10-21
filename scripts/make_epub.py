""" Genereaza EPUB 2 valid din manuscript_official.md (stdlib only). """
import html
import re
import sys
import uuid
import zipfile
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
A = Path(r"C:\Users\bizoi\roman")
SRC = (A / "manuscript_official.md").read_text(encoding="utf-8")
OUTDIR = A / "publish"
OUTDIR.mkdir(exist_ok=True)

BOOK_ID = str(uuid.uuid4())
AUTHOR = "L. T."  # pen-name livrat de user 13 oct
TITLE = "The Glass Crown"
LANG = "en"

def inline(s):
    s = html.escape(s)
    s = re.sub(r"\*\*\*(.+?)\*\*\*", r"<strong><em>\1</em></strong>", s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"\*(.+?)\*", r"<em>\1</em>", s)
    return s

def md_to_body(md):
    out = []
    for line in md.split("\n"):
        s = line.strip()
        if not s:
            continue
        if s == "---":
            out.append("<hr/>")
            continue
        if re.match(r"^#{0,4}\s*\*{0,2}Scene \d+.*$", s):
            out.append('<p style="text-align:center">* * *</p>')
            continue
        m = re.match(r"^(#{1,4})\s+(.*)$", s)
        if m:
            lvl = min(len(m.group(1)) + 1, 4)
            out.append("<h%d>%s</h%d>" % (lvl, inline(m.group(2).strip("*").strip()), lvl))
            continue
        out.append("<p>" + inline(s) + "</p>")
    return "\n".join(out)

# split pe headere ## Chapter N (prima parte = front matter)
chunks = re.split(r"(?m)^## \*{0,2}Chapter (\d+): (.+?)\*{0,2}\s*$", SRC)
front = chunks[0]
files = [("title", "Title Page", front)]
i = 1
while i < len(chunks):
    n, title, body = chunks[i], chunks[i + 1], chunks[i + 2]
    files.append(("ch%02d" % int(n), "Chapter %s: %s" % (n, title.strip()), "## Chapter %s: %s\n\n%s" % (n, title.strip(), body)))
    i += 3
print("sections:", len(files) - 1)
assert len(files) == 11, "astept 10 capitole, am %d" % (len(files) - 1)

# coperta: prima pagina + metadata cover
cover_src = OUTDIR / "cover_front_final.png"
cover_bytes = cover_src.read_bytes() if cover_src.exists() else None

CSS = "body{font-family:serif;line-height:1.5;margin:5%}h1{text-align:center}h2{margin-top:2em}hr{margin:2em 20%}"
MANIFEST = "".join(
    '<item id="%s" href="%s.xhtml" media-type="application/xhtml+xml"/>\n' % (fid, fid) for fid, _, _ in files
) + '<item id="css" href="style.css" media-type="text/css"/>\n<item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml"/>'
if cover_bytes:
    MANIFEST += '<item id="cover-image" href="cover.png" media-type="image/png"/>\n'
    MANIFEST = MANIFEST.replace(
        '<item id="title"',
        '<item id="coverpage" href="cover.xhtml" media-type="application/xhtml+xml"/>\n<item id="title"')

SPINE = "".join('<itemref idref="%s"/>\n' % fid for fid, _, _ in files)
NAV = "".join('<navPoint id="n%s" playOrder="%d"><navLabel><text>%s</text></navLabel><content src="%s.xhtml"/></navPoint>\n'
              % (k, k, html.escape(title), fid) for k, (fid, title, _) in enumerate(files, 1))
if cover_bytes:
    SPINE = '<itemref idref="coverpage"/>\n' + SPINE
    NAV = '<navPoint id="n0" playOrder="0"><navLabel><text>Cover</text></navLabel><content src="cover.xhtml"/></navPoint>\n' + NAV

OPF = """<?xml version="1.0" encoding="utf-8"?>
<package xmlns="http://www.idpf.org/2007/opf" unique-identifier="bookid" version="2.0">
<metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
<dc:title>%(title)s</dc:title>
<dc:creator>%(author)s</dc:creator>
<dc:language>%(lang)s</dc:language>
<dc:identifier id="bookid">urn:uuid:%(bid)s</dc:identifier>
<meta name="cover" content="cover-image"/>
</metadata>
<manifest>
%(manifest)s</manifest>
<spine toc="ncx">
%(spine)s</spine>
</package>""" % {"title": TITLE, "author": AUTHOR, "lang": LANG, "bid": BOOK_ID, "manifest": MANIFEST, "spine": SPINE}

NCX = """<?xml version="1.0" encoding="utf-8"?>
<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">
<head><meta name="dtb:uid" content="urn:uuid:%s"/></head>
<docTitle><text>%s</text></docTitle>
<navMap>
%s</navMap>
</ncx>""" % (BOOK_ID, TITLE, NAV)

CONTAINER = """<?xml version="1.0" encoding="utf-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
<rootfiles><rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/></rootfiles>
</container>"""

PAGE = """<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
<html xmlns="http://www.w3.org/1999/xhtml"><head><title>%s</title><link rel="stylesheet" type="text/css" href="style.css"/></head><body>%s</body></html>"""

epub = OUTDIR / "The_Glass_Crown.epub"
with zipfile.ZipFile(epub, "w") as z:
    z.writestr("mimetype", "application/epub+zip", compress_type=zipfile.ZIP_STORED)
    z.writestr("META-INF/container.xml", CONTAINER, compress_type=zipfile.ZIP_DEFLATED)
    z.writestr("OEBPS/content.opf", OPF, compress_type=zipfile.ZIP_DEFLATED)
    z.writestr("OEBPS/toc.ncx", NCX, compress_type=zipfile.ZIP_DEFLATED)
    z.writestr("OEBPS/style.css", CSS, compress_type=zipfile.ZIP_DEFLATED)
    for fid, title, md in files:
        if md is None:
            continue
        z.writestr("OEBPS/%s.xhtml" % fid, PAGE % (html.escape(title), md_to_body(md)), compress_type=zipfile.ZIP_DEFLATED)
    if cover_bytes:
        z.writestr("OEBPS/cover.png", cover_bytes, compress_type=zipfile.ZIP_DEFLATED)
        z.writestr("OEBPS/cover.xhtml", PAGE % ("Cover", '<div style="text-align:center"><img src="cover.png" alt="cover" style="max-width:100%%"/></div>'), compress_type=zipfile.ZIP_DEFLATED)

# validare: redeschide + parse XML-urile
z = zipfile.ZipFile(epub)
names = z.namelist()
assert names[0] == "mimetype", names[:3]
import xml.dom.minidom as md
md.parseString(z.read("OEBPS/content.opf"))
md.parseString(z.read("OEBPS/toc.ncx"))
for fid, _, _ in files:
    md.parseString(z.read("OEBPS/%s.xhtml" % fid))
print("EPUB valid:", epub, epub.stat().st_size, "bytes,", len(names), "fisiere")
