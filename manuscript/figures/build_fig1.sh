#!/usr/bin/env bash
# Build fig1 (Heil Hitler comparison) and fig2_verbatims (six actionable Grade A cards):
#   render each HTML to PDF + PNG with tight-crop.
#
# Pipeline: Chrome headless → PDF → PyMuPDF → tight-crop PNG.

set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$HERE"

CHROME="/c/Program Files/Google/Chrome/Application/chrome.exe"

if [[ ! -f "$CHROME" ]]; then
  echo "ERROR: Chrome not found at $CHROME" >&2
  exit 1
fi

render_variant () {
  local html="$1"   # filename of the HTML source (e.g. fig1.html)
  local suffix="$2" # query suffix appended to URL (e.g. "" or "?nocaption")
  local base="$3"   # output basename (e.g. fig1, fig1_full)
  local tmppdf="${TMPDIR:-/tmp}/${base}_build.pdf"
  rm -f "$tmppdf"
  local url="file:///$(cygpath -m "$HERE")/${html}${suffix}"
  "$CHROME" --headless=new --disable-gpu --no-sandbox --hide-scrollbars \
            --no-pdf-header-footer \
            --print-to-pdf="$tmppdf" "$url" >/dev/null 2>&1
  # NOTE: do not cp tmppdf to base.pdf yet — first crop, then write base.pdf via PyMuPDF
  local here_win
  here_win="$(cygpath -m "$HERE")"
  local tmppdf_win
  tmppdf_win="$(cygpath -m "$tmppdf")"
  python -X utf8 - <<PY
import pymupdf
import numpy as np
from PIL import Image

src_pdf = r"${tmppdf_win}"
out_pdf = r"${here_win}/${base}.pdf"
out_png = r"${here_win}/${base}.png"

# Render source PDF page 1 to pixmap, find content bbox via PIL
doc = pymupdf.open(src_pdf)
pix = doc[0].get_pixmap(dpi=300)
pix.save(out_png)
img = Image.open(out_png).convert("RGB")
arr = np.asarray(img)
mask = arr.min(axis=2) < 245
rows = np.where(mask.any(axis=1))[0]
cols = np.where(mask.any(axis=0))[0]

if len(rows) and len(cols):
    # Tight-crop PNG
    top, bottom = int(rows[0]), int(rows[-1]) + 1
    left, right = int(cols[0]), int(cols[-1]) + 1
    img.crop((left, top, right, bottom)).save(out_png)
    img = Image.open(out_png)
    # Tight-crop PDF: derive bbox in PDF user-space units, set CropBox
    page = doc[0]
    page_w_pts, page_h_pts = page.rect.width, page.rect.height
    px_w, px_h = pix.width, pix.height
    sx, sy = page_w_pts / px_w, page_h_pts / px_h
    crop_left   = left   * sx
    crop_top    = top    * sy
    crop_right  = right  * sx
    crop_bottom = bottom * sy
    new_rect = pymupdf.Rect(crop_left, crop_top, crop_right, crop_bottom)
    page.set_cropbox(new_rect)
    doc.save(out_pdf, garbage=4, deflate=True)
else:
    doc.save(out_pdf)
doc.close()

print(f"  wrote ${base}.pdf  +  ${base}.png  ({img.width} x {img.height}, tight-crop)")
PY
}

render_variant "fig1.html"            ""           "fig1_full"
render_variant "fig1.html"            "?nocaption" "fig1"
render_variant "fig2_verbatims.html"  ""           "fig2_verbatims_full"
render_variant "fig2_verbatims.html"  "?nocaption" "fig2_verbatims"

echo "Done."
