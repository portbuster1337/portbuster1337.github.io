# portbuster1337.github.io

Static source for [portbuster1337.github.io](https://portbuster1337.github.io).

## Layout

- `index.html`: writing index
- `about.html`: scope, disclosure, contact
- `posts/headless-https-capture.html`: red team analysis of the NetSnitch and HTTP Debugger IPC stack
- `assets/style.css`: black-and-white system-font stylesheet
- `assets/favicon.svg`: local monochrome icon
- `assets/collector-overview.png`, `assets/collector-detail.png`: grayscale collector screenshots from the isolated Any.run test
- `assets/diagrams/`: static Mermaid SVGs, with `.mmd` sources and the generator under `assets/diagrams/src/`
- `404.html`: GitHub Pages not-found page
- `sitemap.xml`, `robots.txt`: crawler metadata
- `.nojekyll`: serve files without Jekyll processing

## Content rules

- Black and white only. No external fonts, analytics, trackers, or third-party assets.
- ASCII only. No em dashes, curly quotes, arrows, or other non-ASCII punctuation in page content.
- Security writing is red team oriented, authorized-use scoped, and written from an operator's perspective. It covers architecture, reverse engineering, operational tradeoffs, and blue team visibility.
- No arming sequences, selector values, persistence recipes, credential theft code, or turnkey intrusion tooling.
- When discussing dual-use techniques, describe the mechanism, the tradeoffs, and the detection signal, not the operational sequence.
- Disassembly is shown as static Mermaid SVGs. Every instruction line has a comment; control flow and calls are linked in the graph. No client-side JavaScript is used to render it.
- Screenshots are grayscale and limited to non-sensitive traffic from an isolated test VM.

## Local preview

```sh
python3 -m http.server 8080
```

Open `http://localhost:8080/`.

## Checks

```sh
# ASCII-only source check
LC_ALL=C grep -RInP '[^\x00-\x7F]' --include='*.html' --include='*.css' --include='*.svg' --include='*.xml' --include='*.txt' .

# Broken local link check (requires a running preview server)
python3 -m http.server 8080 &
python3 - <<'PY'
import re, urllib.request
base = 'http://localhost:8080'
for page in ('/', '/about.html', '/posts/headless-https-capture.html'):
    html = urllib.request.urlopen(base + page).read().decode()
    for href in re.findall(r'href="([^"]+)"', html):
        if href.startswith(('#', 'http://', 'https://', 'mailto:')):
            continue
        url = base + href if href.startswith('/') else base + '/' + href
        print(urllib.request.urlopen(url).status, href)
PY
```

## Deployment

The repository is published with GitHub Pages from the repository root. Push to `main`; Pages builds automatically. The `.nojekyll` file keeps the directory layout exact.
