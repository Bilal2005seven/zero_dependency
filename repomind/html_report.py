"""
html_report.py – Generate a self-contained HTML dashboard for RepoMind.

Public API
----------
    generate_html_report(data: dict, output_path: Path) -> None

Parameters
----------
data : dict
    Must contain the keys produced by repomind.py:
      root, files, total_lines, total_size, all_analysis,
      dependency_graph, cycles, unused_functions,
      all_security_issues, all_functions, health.
output_path : Path
    Destination file (created / overwritten).

Dependencies
------------
Standard library only (json, pathlib, html).
D3.js v7 is loaded from cdn.jsdelivr.net in the browser.
"""

import html
import json
from pathlib import Path


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _esc(text: str) -> str:
    """HTML-escape a string."""
    return html.escape(str(text), quote=True)


def _severity_class(severity: str) -> str:
    return {"HIGH": "sev-high", "MEDIUM": "sev-medium", "LOW": "sev-low"}.get(
        severity.upper(), "sev-low"
    )


def _grade_class(grade: str) -> str:
    return {
        "EXCELLENT": "grade-excellent",
        "GOOD": "grade-good",
        "FAIR": "grade-fair",
        "POOR": "grade-poor",
    }.get(grade.upper(), "grade-fair")


# ---------------------------------------------------------------------------
# Section builders
# ---------------------------------------------------------------------------

def _overview_section(data: dict) -> str:
    health = data["health"]
    gc = _grade_class(health["grade"])
    return f"""
<section class="section" id="sec-overview">
  <h2>Overview</h2>
  <div class="card-grid">
    <div class="card">
      <div class="card-value">{len(data['files'])}</div>
      <div class="card-label">Python Files</div>
    </div>
    <div class="card">
      <div class="card-value">{data['total_lines']:,}</div>
      <div class="card-label">Lines of Code</div>
    </div>
    <div class="card">
      <div class="card-value">{data['total_size']:,}</div>
      <div class="card-label">Total Size (bytes)</div>
    </div>
    <div class="card">
      <div class="card-value {gc}">{health['score']}<span class="card-unit">/100</span></div>
      <div class="card-label">Health Score – {_esc(health['grade'])}</div>
    </div>
    <div class="card">
      <div class="card-value sev-high">{len(data['all_security_issues'])}</div>
      <div class="card-label">Security Issues</div>
    </div>
    <div class="card">
      <div class="card-value">{len(data['cycles'])}</div>
      <div class="card-label">Circular Dependencies</div>
    </div>
    <div class="card">
      <div class="card-value">{len(data['unused_functions'])}</div>
      <div class="card-label">Unused Functions</div>
    </div>
    <div class="card">
      <div class="card-value">{len(data['all_functions'])}</div>
      <div class="card-label">Total Functions</div>
    </div>
  </div>
</section>
"""


def _security_section(data: dict) -> str:
    issues = data["all_security_issues"]
    if not issues:
        body = '<p class="ok-msg">✓ No security issues found.</p>'
    else:
        rows = ""
        for issue in issues:
            sc = _severity_class(issue.get("severity", ""))
            rows += (
                f'<tr>'
                f'<td><span class="badge {sc}">{_esc(issue.get("severity","?"))}</span></td>'
                f'<td>{_esc(issue.get("type","?"))}</td>'
                f'<td class="mono">{_esc(issue.get("file","?"))}</td>'
                f'<td>{_esc(str(issue.get("line","?")))}</td>'
                f'<td>{_esc(issue.get("message",""))}</td>'
                f'</tr>\n'
            )
        body = f"""
<table>
  <thead><tr><th>Severity</th><th>Type</th><th>File</th><th>Line</th><th>Message</th></tr></thead>
  <tbody>{rows}</tbody>
</table>"""
    return f'<section class="section" id="sec-security"><h2>Security Issues</h2>{body}</section>'


def _complexity_section(data: dict) -> str:
    funcs = sorted(data["all_functions"], key=lambda f: -f["complexity"])
    if not funcs:
        return '<section class="section" id="sec-complexity"><h2>Complexity</h2><p class="ok-msg">No functions found.</p></section>'
    max_cc = funcs[0]["complexity"]
    rows = ""
    for f in funcs:
        bar_pct = int(f["complexity"] / max(max_cc, 1) * 100)
        cc_class = "cc-high" if f["complexity"] > 10 else ("cc-medium" if f["complexity"] > 5 else "cc-ok")
        rows += (
            f'<tr>'
            f'<td class="mono">{_esc(f["name"])}</td>'
            f'<td class="mono">{_esc(f["file"])}</td>'
            f'<td>{_esc(str(f["line"]))}</td>'
            f'<td><span class="{cc_class}">{f["complexity"]}</span>'
            f'  <div class="cc-bar"><div class="cc-fill {cc_class}" style="width:{bar_pct}%"></div></div></td>'
            f'</tr>\n'
        )
    return f"""
<section class="section" id="sec-complexity">
  <h2>Complexity (Cyclomatic)</h2>
  <table>
    <thead><tr><th>Function</th><th>File</th><th>Line</th><th>Complexity</th></tr></thead>
    <tbody>{rows}</tbody>
  </table>
</section>"""


def _deadcode_section(data: dict) -> str:
    unused = data["unused_functions"]
    if not unused:
        body = '<p class="ok-msg">✓ No potentially unused functions found.</p>'
    else:
        rows = "".join(
            f'<tr><td class="mono">{_esc(f["name"])}</td>'
            f'<td class="mono">{_esc(f["file"])}</td>'
            f'<td>{_esc(str(f["line"]))}</td></tr>\n'
            for f in unused
        )
        body = f'<table><thead><tr><th>Function</th><th>File</th><th>Line</th></tr></thead><tbody>{rows}</tbody></table>'
    return f'<section class="section" id="sec-deadcode"><h2>Potentially Unused Functions</h2>{body}</section>'


def _cycles_section(data: dict) -> str:
    cycles = data["cycles"]
    if not cycles:
        body = '<p class="ok-msg">✓ No circular dependencies detected.</p>'
    else:
        items = "".join(
            f'<li class="cycle-item">⚠ {_esc(" → ".join(c))}</li>'
            for c in cycles
        )
        body = f'<ul class="cycle-list">{items}</ul>'
    return f'<section class="section" id="sec-cycles"><h2>Circular Dependencies</h2>{body}</section>'


def _files_section(data: dict) -> str:
    rows = "".join(
        f'<tr><td class="mono">{_esc(f["path"])}</td>'
        f'<td>{f["lines"]:,}</td>'
        f'<td>{f["size"]:,}</td></tr>\n'
        for f in sorted(data["files"], key=lambda x: -x["lines"])
    )
    return f"""
<section class="section" id="sec-files">
  <h2>Files</h2>
  <table>
    <thead><tr><th>Path</th><th>Lines</th><th>Size (bytes)</th></tr></thead>
    <tbody>{rows}</tbody>
  </table>
</section>"""


def _graph_section(data: dict) -> str:
    """Interactive D3 force-directed dependency graph."""
    graph = data["dependency_graph"]
    nodes = [{"id": m} for m in graph]
    links = []
    for src, targets in graph.items():
        for tgt in targets:
            links.append({"source": src, "target": tgt})

    graph_json = json.dumps({"nodes": nodes, "links": links})

    return f"""
<section class="section" id="sec-graph">
  <h2>Dependency Graph <span class="graph-hint">(drag nodes · scroll to zoom)</span></h2>
  <div id="graph-container">
    <svg id="dep-graph"></svg>
  </div>
  <script>
  (function(){{
    var graphData = {graph_json};

    function renderGraph() {{
      var container = document.getElementById('graph-container');
      var W = container.clientWidth || 800;
      var H = 520;

      var svg = d3.select('#dep-graph')
        .attr('width', W)
        .attr('height', H);

      svg.selectAll('*').remove();

      // Arrow marker
      svg.append('defs').append('marker')
        .attr('id', 'arrow')
        .attr('viewBox', '0 -5 10 10')
        .attr('refX', 22)
        .attr('refY', 0)
        .attr('markerWidth', 6)
        .attr('markerHeight', 6)
        .attr('orient', 'auto')
        .append('path')
        .attr('d', 'M0,-5L10,0L0,5')
        .attr('fill', '#7c8cf8');

      var g = svg.append('g');

      // Zoom
      svg.call(d3.zoom()
        .scaleExtent([0.3, 3])
        .on('zoom', function(event) {{ g.attr('transform', event.transform); }}));

      var simulation = d3.forceSimulation(graphData.nodes)
        .force('link', d3.forceLink(graphData.links).id(function(d){{ return d.id; }}).distance(140))
        .force('charge', d3.forceManyBody().strength(-320))
        .force('center', d3.forceCenter(W / 2, H / 2))
        .force('collision', d3.forceCollide(50));

      var link = g.append('g').selectAll('line')
        .data(graphData.links)
        .enter().append('line')
        .attr('class', 'graph-link')
        .attr('marker-end', 'url(#arrow)');

      var node = g.append('g').selectAll('g')
        .data(graphData.nodes)
        .enter().append('g')
        .attr('class', 'graph-node')
        .call(d3.drag()
          .on('start', dragstarted)
          .on('drag', dragged)
          .on('end', dragended));

      node.append('circle').attr('r', 18);
      node.append('text')
        .attr('dy', 32)
        .attr('text-anchor', 'middle')
        .text(function(d) {{
          var parts = d.id.split('.');
          return parts[parts.length - 1];
        }});

      node.append('title').text(function(d) {{ return d.id; }});

      simulation.on('tick', function() {{
        link
          .attr('x1', function(d) {{ return d.source.x; }})
          .attr('y1', function(d) {{ return d.source.y; }})
          .attr('x2', function(d) {{ return d.target.x; }})
          .attr('y2', function(d) {{ return d.target.y; }});
        node.attr('transform', function(d) {{
          return 'translate(' + d.x + ',' + d.y + ')';
        }});
      }});

      function dragstarted(event, d) {{
        if (!event.active) simulation.alphaTarget(0.3).restart();
        d.fx = d.x; d.fy = d.y;
      }}
      function dragged(event, d) {{ d.fx = event.x; d.fy = event.y; }}
      function dragended(event, d) {{
        if (!event.active) simulation.alphaTarget(0);
        d.fx = null; d.fy = null;
      }}
    }}

    // Wait for D3 then render
    function tryRender() {{
      if (typeof d3 !== 'undefined') {{ renderGraph(); }}
      else {{ setTimeout(tryRender, 50); }}
    }}
    tryRender();
  }})();
  </script>
</section>"""


# ---------------------------------------------------------------------------
# CSS + page template
# ---------------------------------------------------------------------------

_CSS = """
:root {
  --bg: #0f1117;
  --surface: #1a1d27;
  --surface2: #22263a;
  --border: #2e3251;
  --text: #e2e8f0;
  --text-muted: #8892b0;
  --accent: #7c8cf8;
  --accent2: #a78bfa;
  --ok: #34d399;
  --warn: #fbbf24;
  --danger: #f87171;
  --radius: 12px;
  --shadow: 0 4px 24px rgba(0,0,0,.45);
}

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

body {
  font-family: 'Inter', system-ui, sans-serif;
  background: var(--bg);
  color: var(--text);
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

/* ── Header ── */
header {
  background: linear-gradient(135deg, #1a1d27 0%, #12162b 100%);
  border-bottom: 1px solid var(--border);
  padding: 24px 40px;
  display: flex;
  align-items: center;
  gap: 16px;
}
header .logo {
  font-size: 1.7rem;
  font-weight: 800;
  background: linear-gradient(90deg, var(--accent), var(--accent2));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  letter-spacing: -0.5px;
}
header .subtitle {
  color: var(--text-muted);
  font-size: .9rem;
  margin-left: auto;
}

/* ── Layout ── */
.layout { display: flex; flex: 1; min-height: 0; }

nav {
  width: 220px;
  background: var(--surface);
  border-right: 1px solid var(--border);
  padding: 24px 0;
  position: sticky;
  top: 0;
  height: 100vh;
  overflow-y: auto;
  flex-shrink: 0;
}
nav a {
  display: block;
  padding: 10px 24px;
  color: var(--text-muted);
  text-decoration: none;
  font-size: .9rem;
  border-left: 3px solid transparent;
  transition: all .15s;
}
nav a:hover, nav a.active {
  color: var(--accent);
  border-left-color: var(--accent);
  background: rgba(124,140,248,.07);
}

main { flex: 1; padding: 32px 40px; max-width: 1200px; overflow-x: hidden; }

/* ── Sections ── */
.section { margin-bottom: 48px; }
.section h2 {
  font-size: 1.25rem;
  font-weight: 700;
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 1px solid var(--border);
  color: var(--text);
  display: flex;
  align-items: center;
  gap: 10px;
}
.section h2::before {
  content: '';
  display: inline-block;
  width: 4px;
  height: 1.1em;
  background: linear-gradient(var(--accent), var(--accent2));
  border-radius: 2px;
}

/* ── Cards ── */
.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 16px;
}
.card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 20px 16px;
  text-align: center;
  box-shadow: var(--shadow);
  transition: transform .15s, box-shadow .15s;
}
.card:hover { transform: translateY(-2px); box-shadow: 0 8px 32px rgba(0,0,0,.5); }
.card-value {
  font-size: 2rem;
  font-weight: 800;
  line-height: 1;
  color: var(--accent);
}
.card-unit { font-size: 1rem; font-weight: 500; color: var(--text-muted); }
.card-label { color: var(--text-muted); font-size: .8rem; margin-top: 6px; }

/* ── Tables ── */
table {
  width: 100%;
  border-collapse: collapse;
  font-size: .88rem;
  background: var(--surface);
  border-radius: var(--radius);
  overflow: hidden;
  box-shadow: var(--shadow);
}
thead tr { background: var(--surface2); }
th {
  text-align: left;
  padding: 12px 16px;
  color: var(--text-muted);
  font-weight: 600;
  font-size: .8rem;
  text-transform: uppercase;
  letter-spacing: .05em;
}
td { padding: 10px 16px; border-top: 1px solid var(--border); vertical-align: middle; }
tr:hover td { background: rgba(124,140,248,.05); }
.mono { font-family: 'Fira Code', 'Cascadia Code', monospace; font-size: .83rem; }

/* ── Badges ── */
.badge {
  display: inline-block;
  padding: 2px 10px;
  border-radius: 999px;
  font-size: .75rem;
  font-weight: 700;
  letter-spacing: .05em;
  text-transform: uppercase;
}
.sev-high  { background: rgba(248,113,113,.15); color: var(--danger); }
.sev-medium { background: rgba(251,191,36,.15); color: var(--warn); }
.sev-low   { background: rgba(52,211,153,.15);  color: var(--ok); }

/* ── Grade colours (reuse for card-value) ── */
.grade-excellent { color: var(--ok); }
.grade-good      { color: #86efac; }
.grade-fair      { color: var(--warn); }
.grade-poor      { color: var(--danger); }

/* ── Complexity bars ── */
.cc-bar  { display: inline-block; width: 80px; height: 6px; background: var(--border); border-radius: 3px; margin-left: 8px; vertical-align: middle; }
.cc-fill { height: 100%; border-radius: 3px; }
.cc-ok     { color: var(--ok); background: var(--ok); }
.cc-medium { color: var(--warn); background: var(--warn); }
.cc-high   { color: var(--danger); background: var(--danger); }

/* ── Graph ── */
#graph-container {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  overflow: hidden;
  box-shadow: var(--shadow);
}
#dep-graph { width: 100%; display: block; }
.graph-link { stroke: #7c8cf8; stroke-opacity: .55; stroke-width: 1.5px; fill: none; }
.graph-node circle {
  fill: var(--surface2);
  stroke: var(--accent);
  stroke-width: 2px;
  cursor: grab;
  transition: fill .15s;
}
.graph-node:hover circle { fill: rgba(124,140,248,.25); }
.graph-node text { fill: var(--text-muted); font-size: 11px; pointer-events: none; }
.graph-hint { font-size: .75rem; color: var(--text-muted); font-weight: 400; }

/* ── Cycles ── */
.cycle-list { list-style: none; }
.cycle-item {
  background: rgba(248,113,113,.08);
  border: 1px solid rgba(248,113,113,.3);
  border-radius: 8px;
  padding: 10px 16px;
  margin-bottom: 8px;
  font-family: 'Fira Code', monospace;
  font-size: .85rem;
  color: var(--danger);
}

/* ── ok msg ── */
.ok-msg {
  color: var(--ok);
  background: rgba(52,211,153,.08);
  border: 1px solid rgba(52,211,153,.25);
  border-radius: 8px;
  padding: 12px 16px;
}

@media (max-width: 700px) {
  main { padding: 16px; }
  header { padding: 16px; }
  nav { display: none; }
  .card-grid { grid-template-columns: 1fr 1fr; }
}
"""


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def generate_html_report(data: dict, output_path: Path) -> None:
    """
    Write a self-contained HTML report to *output_path*.

    Parameters
    ----------
    data : dict
        Analysis results as produced by repomind.py.
    output_path : Path
        Destination file path.
    """
    root_label = _esc(data.get("root", ""))

    nav_links = [
        ("#sec-overview",  "Overview"),
        ("#sec-security",  "Security"),
        ("#sec-complexity","Complexity"),
        ("#sec-deadcode",  "Unused Code"),
        ("#sec-cycles",    "Cycles"),
        ("#sec-graph",     "Dep. Graph"),
        ("#sec-files",     "Files"),
    ]
    nav_html = "\n".join(
        f'<a href="{href}">{label}</a>' for href, label in nav_links
    )

    sections = (
        _overview_section(data)
        + _security_section(data)
        + _complexity_section(data)
        + _deadcode_section(data)
        + _cycles_section(data)
        + _graph_section(data)
        + _files_section(data)
    )

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>RepoMind – {root_label}</title>
  <meta name="description" content="RepoMind HTML analysis dashboard for {root_label}">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&family=Fira+Code&display=swap" rel="stylesheet">
  <script src="https://cdn.jsdelivr.net/npm/d3@7/dist/d3.min.js"></script>
  <style>{_CSS}</style>
</head>
<body>
<header>
  <div class="logo">RepoMind</div>
  <div class="subtitle">{root_label}</div>
</header>
<div class="layout">
  <nav id="sidebar">
    {nav_html}
  </nav>
  <main>
    {sections}
  </main>
</div>
<script>
// Highlight active nav link on scroll
(function() {{
  var links = document.querySelectorAll('nav a');
  var sections = Array.from(links).map(function(a) {{
    return document.querySelector(a.getAttribute('href'));
  }});
  function onScroll() {{
    var scrollY = window.scrollY || document.documentElement.scrollTop;
    var current = 0;
    sections.forEach(function(sec, i) {{
      if (sec && sec.offsetTop - 80 <= scrollY) current = i;
    }});
    links.forEach(function(a) {{ a.classList.remove('active'); }});
    links[current].classList.add('active');
  }}
  window.addEventListener('scroll', onScroll, {{passive: true}});
  onScroll();
}})();
</script>
</body>
</html>"""

    output_path = Path(output_path)
    output_path.write_text(html_content, encoding="utf-8")
