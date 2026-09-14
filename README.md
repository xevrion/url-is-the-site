# url-is-the-site

A webpage that lives entirely inside its own link. No server, no hosting, no file
sitting anywhere. You copy the URL, you send it to someone, and their browser
builds the whole page out of the address bar.

## How it works

A normal URL is an address. `https://site.com/page.html` means "go ask that
server for that file". But there is another scheme, `data:`, where the URL is not
an address at all. It carries the content inline:

```
data:text/html;base64,PCFkb2N0eXBlIGh0bWw+...
```

The browser reads the `text/html` bit, decodes the base64 after the comma, and
renders whatever comes out as a page. No network request happens. There is no
server, no file on disk, nothing being fetched. So if you take an entire html
file, base64 it, and glue that prefix on the front, you get a link that IS the
website. That is the whole idea, and it is genuinely about three lines of code:

```python
blob = base64.b64encode(html.encode()).decode()
url = "data:text/html;base64," + blob
```

Everything else in this repo is just making that link shorter.

### making it smaller

Base64 turns every 3 bytes into 4 characters, a flat 33% tax. So `--squish`
gzips the page first, base64s *that*, and wraps it in a tiny loader page which is
itself a data URL. The loader fetches the compressed payload, pipes it through
`DecompressionStream("gzip")` (browsers ship a gunzip for free, you do not need
to write one), then replaces itself with the real page:

```js
fetch("data:application/octet-stream;base64," + payload)
  .then(r => r.blob())
  .then(b => new Response(b.stream().pipeThrough(new DecompressionStream("gzip"))).text())
  .then(html => { document.open(); document.write(html); document.close(); });
```

The `document.open()` before `document.write()` is what actually swaps the page
out. Setting `innerHTML` would not work, script tags injected that way never run.

### the fragment trick

Everything after `#` in a URL is the fragment, and it is purely client side. The
browser never puts it in the HTTP request. That means you can host the 20 line
`index.html` on GitHub Pages, but the actual page content still never touches any
server. The server literally cannot know what page it served you. It only ever
exists in the link you share.

### do you need the hosted page?

No. The plain `data:` link is completely standalone. It carries the page and
everything needed to display it, so it works offline, on a plane, forever, with
nothing on the other end. There is no server to go down.

The hosted loader is only for the `#` mode, and it exists purely as a size
tradeoff. Gzipping cuts the link roughly in half, but something has to run the
gunzip, and that something is the loader page. So you trade being standalone for
a shorter link.

`index.html` itself is also standalone. Save it, open it off your disk with no
internet, and it still packs links for you.

| | standalone | needs a host | link size |
|---|---|---|---|
| `data:` | yes | no | bigger |
| `#` | no | yes | about half |

Live loader: <https://xevrion.github.io/url-is-the-site/>

## Usage

```sh
python3 pack.py site.html            # plain data url
python3 pack.py site.html --squish   # gzip it first, loader unpacks in the browser
python3 pack.py site.html --hash     # payload for index.html, rides after the #
```

Copy the output, paste it in the address bar, hit enter. For `--hash`, stick the
output on the end of the loader URL instead.

`site.html` is a small demo page to try it on, swap in your own.

## Limits

- URL length caps are not a spec thing, they are per browser. Chrome handles a
  couple megabytes in the address bar, Firefox is fine too, but random chat apps
  and email clients will mangle anything long.
- Data URLs get a null origin, so no localStorage, no cookies, no fetch to your
  own stuff.
- The page cannot update itself. The link is the version.

See `notes.md` for the things I tripped over.
