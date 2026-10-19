# portbuster1337.github.io

Static source for [portbuster1337.github.io](https://portbuster1337.github.io).

## Layout

- `index.html`: writing index
- `about.html`: scope, disclosure, contact
- `posts/headless-https-capture.html`: NetSnitch and HTTP Debugger IPC analysis
- `assets/style.css`: black-and-white system-font stylesheet
- `assets/favicon.svg`: local monochrome icon
- `404.html`: GitHub Pages not-found page
- `sitemap.xml`, `robots.txt`: crawler metadata
- `.nojekyll`: serve files without Jekyll processing

## Content rules

- Black and white only. No external fonts, analytics, trackers, or third-party assets.
- ASCII only. No em dashes, curly quotes, arrows, or other non-ASCII punctuation in page content.
- Security writing is defensive and authorized-use scoped. No arming sequences, persistence recipes, credential theft code, or turnkey intrusion tooling.
- When discussing dual-use techniques, describe the mechanism and the detection signal, not the operational sequence.

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
