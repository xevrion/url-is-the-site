# url-is-the-site

A webpage that lives entirely inside its own link. No server, no hosting, no file
sitting anywhere. You copy the URL, you send it to someone, and their browser
builds the whole page out of the address bar.

## How it works

Browsers understand `data:` URLs. Instead of pointing at a file somewhere, a data
URL just carries the content itself:

```
data:text/html;base64,PCFkb2N0eXBlIGh0bWw+...
```

Paste that into the address bar and the browser renders it as a page. So if you
take an html file, base64 it, and glue that prefix on the front, you get a link
that IS the website.

`pack.py` does exactly that, in three flavours.

## Usage

```sh
python3 pack.py site.html            # plain data url
python3 pack.py site.html --squish   # gzip it first, loader unpacks in the browser
python3 pack.py site.html --hash     # payload for index.html, rides after the #
```

Copy the output, paste it in the address bar, hit enter.

The `--squish` mode wraps your page in a tiny loader that uses `DecompressionStream`
to unzip the payload client side. Barely helps on small files (the base64 tax eats
the gain) but on anything real it cuts the link roughly in half.

The `--hash` mode is my favourite. Everything after `#` in a URL never leaves your
machine, browsers do not send it to the server. So you can host the 20 line
`index.html` anywhere and the actual page still only exists in the link you share.

## Limits

- URL length caps are not a spec thing, they are per browser. Chrome handles a
  couple megabytes in the address bar, Firefox is fine too, but random chat apps
  and email clients will mangle anything long.
- Data URLs get a null origin, so no localStorage, no cookies, no fetch to your
  own stuff.
- The page cannot update itself. The link is the version.

See `notes.md` for the things I tripped over.
