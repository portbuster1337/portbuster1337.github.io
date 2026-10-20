# Diagram sources

The `.mmd` files are the Mermaid sources for the static SVGs in the parent
directory. The page imports only the rendered SVGs; it does not run Mermaid in
the browser.

- `gen_flows.py` writes the six instruction-flow sources into this directory.
- `architecture.mmd` and `service-call-graph.mmd` are maintained by hand.
- `config-flow.json` sets the white and black theme, system fonts, left-aligned
  node text, and monospace instructions.

Rendering uses the Mermaid CLI and a local Chromium executable:

```sh
node /tmp/opencode/mm/node_modules/.bin/mmdc \
  -c config-flow.json \
  -p /tmp/opencode/mm/puppeteer.json \
  -i service-entry-flow.mmd \
  -o ../service-entry-flow.svg
```

Run `python3 postprocess.py` after rendering. It sets the SVG's intrinsic size,
removes inline max-width and unused shadow filters, and keeps the output ASCII
and self-contained.

All instruction lines in the generated flows carry a `//` comment. The call
graph groups three adjacent calls in one node for layout; the caption in the
article says so.
