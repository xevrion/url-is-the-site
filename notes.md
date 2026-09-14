# notes

Stuff I learned or got bitten by while making this.

### base64 costs you 33%

Every 3 bytes become 4 characters. So a 1KB page is already a 1.4KB link before
anything else. Gzipping first is what makes it worth it, text compresses well
enough that even after the base64 tax you come out ahead, as long as the page is
big enough for the loader boilerplate to pay for itself.

On my tiny `site.html` (1285 bytes) the numbers were:

| mode | url length |
|---|---|
| plain | 1738 |
| squish | 1690 |
| hash | 1007 |

Barely a win for squish at this size. The gzip header plus the loader script is
roughly 400 chars of fixed cost. On a 20KB page the gap gets huge.

### DecompressionStream is free gunzip

I assumed I would have to ship an inflate implementation in the loader. Turns out
browsers already expose `DecompressionStream("gzip")`. Combined with fetching the
payload as its own `data:` URL, unpacking is about four lines:

```js
fetch("data:application/octet-stream;base64," + payload)
  .then(r => r.blob())
  .then(b => new Response(b.stream().pipeThrough(new DecompressionStream("gzip"))).text())
  .then(html => { document.open(); document.write(html); document.close(); })
```

`document.write` after `document.open()` is the bit that actually swaps the page
out. Setting `innerHTML` does not work here because injected script tags do not
run that way.

### the # trick

Anything after `#` is the fragment, and it is purely client side. The browser
never puts it in the HTTP request. So `index.html` can be hosted on GitHub Pages
and the actual content still never touches a server. Feels like cheating but it
is not, the page really is in the link.

Had to `urlencode` the base64 though. `+` and `/` are legal base64 but mean other
things in a URL, and `+` silently became a space the first time I tried it. Took
me a bit to spot because gzip just threw an unhelpful error.

### origins

Data URLs get a null origin. No localStorage, no cookies, no same-origin fetch.
Makes sense in hindsight, a page with no home cannot have a home directory.

### how long can a url be?

There is no limit in the spec. It is entirely down to the browser. Chrome is
happy into the megabytes in the address bar, though it truncates what it displays.
The real limit is everything else in the chain, chat apps and email clients will
happily chop your link in half.

### to try later

- squeeze an actual useful tool in here, a notes app or a calculator
- see how far brotli gets over gzip (`CompressionStream` supports it in newer Chrome)
- the obvious final boss: make it a quine, a page that renders its own URL as text
