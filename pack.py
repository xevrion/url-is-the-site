#!/usr/bin/env python3
"""Turn an html file into a link that carries the whole page inside it.

usage:
    python3 pack.py site.html            plain, one big base64 data url
    python3 pack.py site.html --squish   gzip first, tiny loader unpacks it
    python3 pack.py site.html --hash     payload for index.html, goes after the #
"""

import base64
import gzip
import sys
from urllib.parse import quote

LOADER = """<!doctype html><meta charset=utf-8><script>
fetch("data:application/octet-stream;base64,{payload}")
  .then(r => r.blob())
  .then(b => new Response(b.stream().pipeThrough(new DecompressionStream("gzip"))).text())
  .then(html => { document.open(); document.write(html); document.close(); });
</script>"""


def to_data_url(html):
    blob = base64.b64encode(html.encode()).decode()
    return "data:text/html;base64," + blob


def squish(html):
    packed = gzip.compress(html.encode(), 9)
    payload = base64.b64encode(packed).decode()
    return to_data_url(LOADER.replace("{payload}", payload))


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        return 1

    path = args[0]
    html = open(path).read()

    if "--squish" in args:
        url = squish(html)
    elif "--hash" in args:
        blob = base64.b64encode(gzip.compress(html.encode(), 9)).decode()
        url = "#" + quote(blob, safe="")
    else:
        url = to_data_url(html)

    sys.stderr.write(
        "source: {} bytes\nurl:    {} chars\n\n".format(len(html), len(url))
    )
    print(url)

    if len(url) > 1_800_000:
        sys.stderr.write("\nheads up: that is longer than most browsers accept\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
