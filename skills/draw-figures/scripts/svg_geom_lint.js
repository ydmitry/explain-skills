// Measures every inline figure of the page it runs in and returns a list of findings.
// `figures.py check` builds that page from the figure files and runs this in a headless browser.
// Distances are in viewBox units. Tiers: error (blocks), warn (fix or give the reason), advisory.
//
//   outside-viewbox [error]   a drawn box leaves the <svg> box, so it is clipped
//   text-collision  [error when two <text> boxes overlap, warn when the gap is under 3u]
//   split-label     [warn]    two sibling <text> that are one label: merge them into tspans (S4 §8)
//   edge-through-node [error] an arrowed edge crosses the inside of a labelled node that is not its end
//   arrowhead-hidden [warn]   an arrowhead lands inside a shape painted after the edge
//   node-gap        [warn]    two nodes of the edge manifest touch or sit under 6u apart
//   zone-invisible  [warn]    a zone whose fill cannot be told from its ground, with no visible border
//   text-too-small  [error]   text drawn under 9.5 CSS px
//   manifest-edge-mismatch [error], manifest-entry-unparsable [error], edge-not-in-manifest [warn],
//   manifest-missing [warn], manifest-name-unresolved / -ambiguous [warn]   the edge manifest (S4 §9)
//   text-overflows-container [warn], line-through-text [warn], dead-canvas [warn]
//   arrow-buried, arrow-into-void, text-vs-marker [advisory]
() => {
  const issues = [];
  const push = (tier, obj) => issues.push(Object.assign({ tier }, obj));
  const svgs = [...document.querySelectorAll('svg')];
  svgs.forEach((svg, si) => {
    if (svg.closest('[aria-hidden="true"]')) return;   // decoration, not a figure
    const sr = svg.getBoundingClientRect();
    if (sr.width < 40 || sr.height < 40) return;                             // icons
    const name = svg.id || ('svg#' + si);

    const vb = svg.viewBox && svg.viewBox.baseVal;
    if (!vb || !vb.width) return;                              // the source check reports no-viewbox
    const scale = sr.width / vb.width;
    const svgArea = sr.width * sr.height;

    // ---- measured geometry --------------------------------------------------
    const els = [...svg.querySelectorAll('text, rect, circle, ellipse, line, path, polyline, polygon, image')]
      .filter(el => !el.closest('defs'));
    const texts = [], rects = [], all = [];
    for (const el of els) {
      const r = el.getBoundingClientRect();
      if (r.width === 0 && r.height === 0) continue;
      all.push({ el, r, tag: el.tagName });
      // 1. containment — the svg clips: anything escaping IS cropped in the render
      const over = {
        left:   +((sr.left - r.left)     / scale).toFixed(1),
        top:    +((sr.top - r.top)       / scale).toFixed(1),
        right:  +((r.right - sr.right)   / scale).toFixed(1),
        bottom: +((r.bottom - sr.bottom) / scale).toFixed(1),
      };
      const worst = Math.max(over.left, over.top, over.right, over.bottom);
      if (worst > 1.5) {
        push('error', { svg: name, type: 'outside-viewbox', el: el.tagName,
          text: (el.textContent || '').trim().slice(0, 60), overflow_units: over });
      }
      if (el.tagName === 'text') texts.push({ el, r });
      if (el.tagName === 'rect') rects.push({ el, r });
    }
    // 2. text-vs-text proximity. A same-parent pair that is really ONE logical
    // label split across siblings (stacked two-liner whose em-boxes touch at
    // normal leading, or value+unit on one baseline) is reported as
    // split-label [warn] with merge advice — the em-box artifact on stacked
    // 12px lines measures as gap<0 while the ink never touches. Deep stacked
    // overlaps (< -4u) and everything cross-parent keep the true tier.
    for (let i = 0; i < texts.length; i++) {
      for (let j = i + 1; j < texts.length; j++) {
        const a = texts[i].r, b = texts[j].r;
        const gapX = Math.max(a.left, b.left) - Math.min(a.right, b.right);
        const gapY = Math.max(a.top, b.top) - Math.min(a.bottom, b.bottom);
        const sep = Math.max(gapX, gapY) / scale;   // <0 = true overlap
        if (sep < 3) {
          const sameParent = texts[i].el.parentNode === texts[j].el.parentNode;
          // centered, left- or right-aligned stack. Two lines of one label share an x, so when the
          // boxes do not even touch (sep >= 0) only a pair lined up within a unit counts as one label:
          // a row's label and the value at the end of its bar are near each other and are two labels.
          const tol = sep >= 0 ? 1 : 4;
          const aligned =
            Math.abs((a.left + a.right) - (b.left + b.right)) / 2 / scale < tol ||
            Math.abs(a.left - b.left) / scale < tol ||
            Math.abs(a.right - b.right) / scale < tol;
          const stacked = gapY >= gapX && aligned;
          const sameBaseline = gapX >= gapY &&
            Math.abs(a.bottom - b.bottom) / scale < 2;
          if (sameParent && ((stacked && sep > -4) || (sameBaseline && sep >= 0))) {
            push('warn', { svg: name, type: 'split-label',
              gap_units: +sep.toFixed(2),
              a: texts[i].el.textContent.trim().slice(0, 36),
              b: texts[j].el.textContent.trim().slice(0, 36),
              detail: 'one logical label = one <text> (S4 §8): merge these siblings into tspans of a single <text>' });
          } else {
            push(sep < 0 ? 'error' : 'warn', { svg: name, type: 'text-collision',
              gap_units: +sep.toFixed(2),
              a: texts[i].el.textContent.trim().slice(0, 36),
              b: texts[j].el.textContent.trim().slice(0, 36),
              detail: sep < 0 ? 'the two labels overlap: move one' :
                'the two labels do not touch but stand under 3 units apart: move one away' });
          }
        }
      }
    }
    // 3. rendered font size
    // The first finding of a figure carries the fix, computed from this figure's own scale: a figure drawn at a
    // viewBox wider than it is shown (scale < 1) shrinks every font by that factor, so the cure is one decision
    // (a viewBox about as wide as the display, or every font-size at or above 9.5 / scale), not 30 edits.
    const small = texts.map(t => ({ t, fs: parseFloat(getComputedStyle(t.el).fontSize) * scale })).filter(x => x.fs < 9.5);
    small.forEach(({ t, fs }, i) => push('error', { svg: name, type: 'text-too-small',
      rendered_px: +fs.toFixed(1), text: t.el.textContent.trim().slice(0, 40),
      ...(i === 0 ? { detail: `${small.length} text(s) in this figure render under 9.5px: it is drawn at viewBox width ` +
        `${+vb.width.toFixed(0)}u and shown at ${+sr.width.toFixed(0)}px (scale ${scale.toFixed(2)}), so a font-size under ` +
        `${(9.5 / scale).toFixed(1)}u is too small. Fix once: draw the figure on a viewBox about as wide as it is shown ` +
        `(then 12-13u text renders at 12-13px), or raise every font-size to at least ${(9.5 / scale).toFixed(1)}u and re-space the labels; ` +
        `do not edit text one at a time` } : {}) }));
    // ---- shared paint-order helpers (used by sections 4b, 8, and 6b) --------
    const docIdx = new Map();
    all.forEach((x, i) => docIdx.set(x.el, i));                  // querySelectorAll order = paint order
    const parseRGB = s => {
      if (!s) return null;
      let mm = s.match(/rgba?\((\d+),\s*(\d+),\s*(\d+)(?:,\s*([\d.]+))?\)/);
      if (mm) return { r: +mm[1], g: +mm[2], b: +mm[3], a: mm[4] === undefined ? 1 : +mm[4] };
      mm = s.match(/color\(srgb\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)(?:\s*\/\s*([\d.]+))?\)/);
      if (mm) return { r: Math.round(255 * mm[1]), g: Math.round(255 * mm[2]), b: Math.round(255 * mm[3]),
                       a: mm[4] === undefined ? 1 : +mm[4] };   // color-mix() computes to color(srgb ...)
      return null;
    };
    const fillAlpha = el => {
      const cs = getComputedStyle(el);
      if (cs.fill === 'none') return 0;
      const c = parseRGB(cs.fill);                               // rgb() = opaque; rgba() carries alpha
      return (c ? c.a : 1) * parseFloat(cs.fillOpacity || 1) * parseFloat(cs.opacity || 1);
    };
    const opaqueShapes = all.filter(x =>
      ['rect', 'circle', 'ellipse', 'polygon'].includes(x.tag) && fillAlpha(x.el) >= 0.5);
    const legendRe = /legend|key/i;
    const inLegendGroup = el => {
      for (let n = el; n && n !== svg; n = n.parentElement) {
        const idc = ((n.getAttribute && n.getAttribute('id')) || '') + ' ' +
                    ((n.getAttribute && n.getAttribute('class')) || '');
        if (legendRe.test(idc)) return true;
      }
      return false;
    };

    // 4. arrow endpoints: buried inside a foreground rect, or pointing at nothing.
    // Collect every marker-end edge once (endpoint = arrowhead tip, start = origin);
    // the manifest diff (section 9) reuses this list.
    const fg = rects.filter(x => (x.r.width * x.r.height) < 0.4 * svgArea);
    // 2D shapes + labels an arrow can legitimately point at (1D strokes excluded:
    // a diagonal line's bbox is a poor proximity proxy)
    const targets = all.filter(x => ['text', 'rect', 'circle', 'ellipse', 'polygon', 'image'].includes(x.tag));
    const arrowEdges = [];
    for (const el of svg.querySelectorAll('line[marker-end], path[marker-end], polyline[marker-end]')) {
      if (el.closest('defs')) continue;
      let x, y, x0, y0;
      try {
        if (el.tagName === 'line') {
          x = el.x2.baseVal.value;  y = el.y2.baseVal.value;
          x0 = el.x1.baseVal.value; y0 = el.y1.baseVal.value;
        } else {
          const L = el.getTotalLength(); if (!L) continue;
          const pe = el.getPointAtLength(L), ps = el.getPointAtLength(0);
          x = pe.x; y = pe.y; x0 = ps.x; y0 = ps.y;
        }
      } catch (e) { continue; }
      const m = el.getScreenCTM();
      arrowEdges.push({ el,
        ex: m.a * x + m.c * y + m.e,   ey: m.b * x + m.d * y + m.f,
        sx: m.a * x0 + m.c * y0 + m.e, sy: m.b * x0 + m.d * y0 + m.f });
    }
    // nearest 2D shape/label to a point — shared by arrow checks + manifest reporting.
    // A bare shape borrows the label whose center sits inside it, so reports read
    // "gamma -> beta" instead of "rect -> rect".
    const labelFor = x => {
      const own = (x.el.textContent || '').trim();
      if (own) return own.slice(0, 30);
      for (const t of texts) {
        const cx = (t.r.left + t.r.right) / 2, cy = (t.r.top + t.r.bottom) / 2;
        if (cx > x.r.left && cx < x.r.right && cy > x.r.top && cy < x.r.bottom) {
          return t.el.textContent.trim().slice(0, 30);
        }
      }
      return x.tag || (x.el && x.el.tagName) || 'shape';
    };
    const nearestTarget = (px, py, self) => {
      let best = Infinity, lbl = '';
      for (const t of targets) {
        if (t.el === self) continue;
        const r = t.r;
        const dx = Math.max(r.left - px, 0, px - r.right);
        const dy = Math.max(r.top - py, 0, py - r.bottom);
        const dist = Math.hypot(dx, dy) / scale;
        if (dist < best) {
          best = dist;
          lbl = labelFor(t) || t.tag;
        }
      }
      return { dist: best, lbl };
    };
    // legend/key swatches are not topology: an edge inside a legend group, or a
    // short swatch line with its key label right beside it, is excluded from
    // the into-void check and the manifest diff below. A short arrow that joins
    // two different shapes is topology, not a key: the gap between adjacent boxes
    // in a row is under 26u and the boxes' own labels sit right beside the arrow
    const shapeTags = ['rect', 'circle', 'ellipse', 'polygon'];
    const joinable = all.filter(x => shapeTags.includes(x.tag) && (x.r.width * x.r.height) < 0.4 * svgArea);
    const shapesNear = (px, py) => joinable.filter(x =>
      Math.hypot(Math.max(x.r.left - px, 0, px - x.r.right), Math.max(x.r.top - py, 0, py - x.r.bottom)) / scale <= 8);
    for (const ed of arrowEdges) {
      const lenU = Math.hypot(ed.ex - ed.sx, ed.ey - ed.sy) / scale;
      let swatch = false;
      if (lenU < 26) {
        const mx = (ed.sx + ed.ex) / 2, my = (ed.sy + ed.ey) / 2;
        for (const t of texts) {
          const dy = Math.abs((t.r.top + t.r.bottom) / 2 - my) / scale;
          const dx = Math.max(t.r.left - mx, 0, mx - t.r.right) / scale;
          if (dy < 10 && dx < 30) { swatch = true; break; }
        }
        if (swatch) {
          const a = shapesNear(ed.sx, ed.sy), b = shapesNear(ed.ex, ed.ey);
          if (a.some(x => b.some(y => x !== y))) swatch = false;
        }
      }
      ed.legend = inLegendGroup(ed.el) || swatch;
    }
    for (const ed of arrowEdges) {
      if (ed.legend) continue;
      const px = ed.ex, py = ed.ey;
      let buried = false;
      for (const rr of fg) {
        const r = rr.r, d = 3 * scale;
        if (px > r.left + d && px < r.right - d && py > r.top + d && py < r.bottom - d) {
          const depth = Math.min(px - r.left, r.right - px, py - r.top, r.bottom - py) / scale;
          push('advisory', { svg: name, type: 'arrow-buried',
            into: (rr.el.textContent || rr.el.getAttribute('class') || 'rect').trim().slice(0, 30),
            depth_units: +depth.toFixed(1) });
          buried = true;
          break;
        }
      }
      if (buried) continue;
      // into-void: distance from the endpoint to the nearest 2D shape/label bbox
      const near = nearestTarget(px, py, ed.el);
      if (targets.length && near.dist > 8) {
        push('advisory', { svg: name, type: 'arrow-into-void',
          nearest: near.lbl, dist_units: +near.dist.toFixed(1) });
      }
    }
    // 4b. edge-through-node + arrowhead-hidden. Loop-back/return edges that
    // "slice through" a node, and arrowheads that land inside a node painted
    // after the edge (the S4 decoration-under-nodes z-order hides the marker),
    // both render fine and pass every endpoint tolerance. Node boxes = opaque rects carrying a label.
    const nodeBoxes = rects.filter(x => {
      if ((x.r.width * x.r.height) >= 0.4 * svgArea) return false;
      if (fillAlpha(x.el) < 0.5) return false;                   // zone tints are crossable
      for (const t of texts) {
        const cx = (t.r.left + t.r.right) / 2, cy = (t.r.top + t.r.bottom) / 2;
        if (cx > x.r.left && cx < x.r.right && cy > x.r.top && cy < x.r.bottom) return true;
      }
      return false;
    });
    for (const ed of arrowEdges) {
      if (ed.legend) continue;
      // arrowhead-hidden: endpoint inside an opaque shape painted after the edge
      const edIdx = docIdx.get(ed.el) ?? -1;
      for (const sh of opaqueShapes) {
        if (sh.el === ed.el || docIdx.get(sh.el) < edIdx) continue;
        const d = 1 * scale;
        if (ed.ex > sh.r.left + d && ed.ex < sh.r.right - d &&
            ed.ey > sh.r.top + d && ed.ey < sh.r.bottom - d) {
          push('warn', { svg: name, type: 'arrowhead-hidden',
            under: labelFor(sh),
            detail: 'the marker paints UNDER this shape (decoration-first z-order): land 2-4px short OUTSIDE the border' });
          break;
        }
      }
      // edge-through-node: sample the path; a contiguous run through a node
      // interior that is not a landing overshoot means the edge crosses it
      let L, m;
      try { L = ed.el.getTotalLength(); } catch (e) { continue; }
      if (!L) continue;
      m = ed.el.getScreenCTM();
      const at = u => { const p = ed.el.getPointAtLength(u);
        return { x: m.a * p.x + m.c * p.y + m.e, y: m.b * p.x + m.d * p.y + m.f }; };
      for (const nb of nodeBoxes) {
        const r = nb.r, d = 1 * scale, pad = 2 * scale;
        const inside = p => p.x > r.left + d && p.x < r.right - d && p.y > r.top + d && p.y < r.bottom - d;
        const containsPt = (px, py) => px > r.left - pad && px < r.right + pad && py > r.top - pad && py < r.bottom + pad;
        if (containsPt(ed.sx, ed.sy)) continue;                  // source box (or container holding the start)
        const endInside = containsPt(ed.ex, ed.ey);
        const step = Math.max(2, L / 500);
        let run = 0, worst = 0;
        for (let u = 0; u <= L; u += step) {
          if (inside(at(u))) { run += step; if (run > worst) worst = run; }
          else run = 0;
        }
        const worstU = worst;                                     // getPointAtLength walks user units
        if ((endInside && worstU > 18) || (!endInside && worstU > 14)) {
          push('error', { svg: name, type: 'edge-through-node',
            node: labelFor(nb), run_units: +worstU.toFixed(0),
            detail: endInside
              ? 'the edge enters this node and travels through its interior before stopping — land 2-4px short of the port instead'
              : 'the edge transits this node\'s interior — route around it (S4 §3 corridors) or via different ports' });
          break;
        }
      }
    }
    // 5. text vs small marks (dots, ticks): true 2D intersection only
    const marks = all.filter(x =>
      ((x.tag === 'circle' || x.tag === 'ellipse') && x.r.width <= 24 * scale && x.r.height <= 24 * scale) ||
      (x.tag === 'rect' && x.r.width <= 14 * scale && x.r.height <= 14 * scale));
    for (const t of texts) {
      for (const mk of marks) {
        const ox = Math.min(t.r.right, mk.r.right) - Math.max(t.r.left, mk.r.left);
        const oy = Math.min(t.r.bottom, mk.r.bottom) - Math.max(t.r.top, mk.r.top);
        if (ox > 0 && oy > 0) {
          push('advisory', { svg: name, type: 'text-vs-marker',
            text: t.el.textContent.trim().slice(0, 36), mark: mk.tag,
            overlap_units: +(Math.min(ox, oy) / scale).toFixed(1) });
        }
      }
    }
    // 6. dead canvas: union of content boxes vs the viewBox, plus the largest
    // empty vertical run (catches content-top/caption-bottom sandwiches).
    // Background panels (>= 60% of the svg area) are excluded so a full-bleed
    // card can't mask emptiness behind it. Whitespace outside the <svg>
    // is out of scope here.
    const content = all.filter(x => (x.r.width * x.r.height) < 0.6 * svgArea);
    if (content.length >= 3) {
      const u = content.reduce((acc, x) => ({
        left: Math.min(acc.left, x.r.left), top: Math.min(acc.top, x.r.top),
        right: Math.max(acc.right, x.r.right), bottom: Math.max(acc.bottom, x.r.bottom),
      }), { left: Infinity, top: Infinity, right: -Infinity, bottom: -Infinity });
      const utilW = Math.min(1, (u.right - u.left) / sr.width);
      const utilH = Math.min(1, (u.bottom - u.top) / sr.height);
      const rows = content.map(x => [Math.max(x.r.top, sr.top), Math.min(x.r.bottom, sr.bottom)])
        .sort((a, b) => a[0] - b[0]);
      let gap = 0, cur = sr.top;
      for (const [t, b] of rows) { if (t - cur > gap) gap = t - cur; if (b > cur) cur = b; }
      if (sr.bottom - cur > gap) gap = sr.bottom - cur;
      const gapFrac = gap / sr.height;
      if (utilW < 0.7 || utilH < 0.7 || gapFrac > 0.3) {
        push('warn', { svg: name, type: 'dead-canvas',
          util_w: +utilW.toFixed(2), util_h: +utilH.toFixed(2), max_empty_run: +gapFrac.toFixed(2),
          detail: 'compute the viewBox from the content bands (S4 - bands first, H last)' });
      }
    }
    // 6b. zone-invisible: a large zone/band rect whose composited fill is
    // imperceptible against its backdrop and that has no visible stroke.
    // The claim-carrying element (a stale window, a phase band) disappears
    // while the caption asserts it exists.
    // effective backdrop = nearest HTML ancestor with an opaque background
    // (the figure sits on a panel of the --surface colour, not on the body)
    let bodyBg = null;
    for (let n = svg.parentElement; n && n !== document.documentElement; n = n.parentElement) {
      const c = parseRGB(getComputedStyle(n).backgroundColor);
      if (c && c.a > 0.9) { bodyBg = c; break; }
    }
    if (!bodyBg) bodyBg = parseRGB(getComputedStyle(document.body).backgroundColor) || { r: 255, g: 255, b: 255, a: 1 };
    for (const z of rects) {
      const zr = z.r, zA = zr.width * zr.height;
      if (zA >= 0.9 * svgArea || zA < 0.03 * svgArea) continue;
      if (zr.width < 0.25 * sr.width && zr.height < 0.25 * sr.height) continue;
      const cs = getComputedStyle(z.el);
      const alpha = fillAlpha(z.el);
      if (alpha === 0) continue;                                 // stroke-only outline boxes are visible by stroke
      const strokeA = cs.stroke === 'none' ? 0 :
        (parseRGB(cs.stroke) || { a: 1 }).a * parseFloat(cs.strokeOpacity || 1) * parseFloat(cs.opacity || 1);
      // a visible stroke saves a boxy container, but NOT a wide band whose
      // whole point is its shading
      const bandLike = zr.width >= 0.4 * sr.width && zr.width / Math.max(1, zr.height) >= 2.5;
      if (strokeA >= 0.2 && parseFloat(cs.strokeWidth || 0) >= 0.75 && !bandLike) continue;
      const zi = docIdx.get(z.el);
      let base = bodyBg;
      let bestA = Infinity;
      const zcx = (zr.left + zr.right) / 2, zcy = (zr.top + zr.bottom) / 2;
      for (const sh of opaqueShapes) {                            // deepest opaque rect under it
        if (sh.el === z.el || docIdx.get(sh.el) >= zi || sh.tag !== 'rect') continue;
        const r = sh.r;
        if (zcx > r.left && zcx < r.right && zcy > r.top && zcy < r.bottom && fillAlpha(sh.el) >= 0.9) {
          const a = r.width * r.height;
          if (a < bestA) { bestA = a; base = parseRGB(getComputedStyle(sh.el).fill) || base; }
        }
      }
      const zc = parseRGB(cs.fill);
      if (!zc) continue;
      const comp = c => Math.round(alpha * zc[c] + (1 - alpha) * base[c]);
      const delta = Math.max(Math.abs(comp('r') - base.r), Math.abs(comp('g') - base.g), Math.abs(comp('b') - base.b));
      if (delta < 8) {
        push('warn', { svg: name, type: 'zone-invisible',
          zone: labelFor(z), delta_rgb: delta,
          detail: 'the zone fill is imperceptible against its backdrop: use a valence tint >= 10% color-mix plus a boundary rule or bracket (S6)' });
      }
    }
    // 7. text overflows its container: a label whose center sits inside a rect
    // but whose box escapes that rect's border by > 2u — the box was sized
    // smaller than its label. Smallest containing
    // rect wins, so a pill label straddling a card edge doesn't false-fire.
    for (const t of texts) {
      const tr = t.r;
      const tcx = (tr.left + tr.right) / 2, tcy = (tr.top + tr.bottom) / 2;
      const tArea = tr.width * tr.height;
      let box = null;
      for (const rr of rects) {
        const r = rr.r, a = r.width * r.height;
        if (a >= 0.9 * svgArea || a < 1.5 * tArea) continue;   // page background / smaller than the label
        if (tcx > r.left && tcx < r.right && tcy > r.top && tcy < r.bottom) {
          if (!box || a < box.a) box = { r, a };
        }
      }
      if (!box) continue;
      const out = Math.max(box.r.left - tr.left, tr.right - box.r.right,
                           box.r.top - tr.top, tr.bottom - box.r.bottom) / scale;
      if (out > 2) {
        push('warn', { svg: name, type: 'text-overflows-container',
          text: t.el.textContent.trim().slice(0, 40), overflow_units: +out.toFixed(1),
          detail: 'size the box from the S4 char-width coefficients, or shorten the label' });
      }
    }
    // 8. line through text: a stroked line/path crossing a label's box (a
    // dashed boundary striking through a label). Both endpoints
    // must lie OUTSIDE the label (a leader line terminating at its label is
    // fine); halo'd labels (S4: paint-order stroke) are exempt by design, and
    // so is a crossing hidden behind an opaque shape painted after the line
    // (a track line running under station boxes is not a visible crossing).
    const halod = el => {
      const cs = getComputedStyle(el);
      return cs.paintOrder.includes('stroke') && cs.stroke !== 'none' && parseFloat(cs.strokeWidth) >= 1.5;
    };
    const strokedLines = all.filter(x =>
      ['line', 'path', 'polyline'].includes(x.tag) &&
      getComputedStyle(x.el).stroke !== 'none');
    for (const t of texts) {
      if (halod(t.el)) continue;
      const pad = 2 * scale;
      const inner = { l: t.r.left + pad, t: t.r.top + pad, r: t.r.right - pad, b: t.r.bottom - pad };
      if (inner.r <= inner.l || inner.b <= inner.t) continue;
      const outer = { l: t.r.left - pad, t: t.r.top - pad, r: t.r.right + pad, b: t.r.bottom + pad };
      for (const s of strokedLines) {
        if (s.r.right < outer.l || s.r.left > outer.r || s.r.bottom < outer.t || s.r.top > outer.b) continue;
        let L;
        try { L = s.el.getTotalLength(); } catch (e) { continue; }
        if (!L) continue;
        const m = s.el.getScreenCTM();
        const at = u => { const p = s.el.getPointAtLength(u);
          return { x: m.a * p.x + m.c * p.y + m.e, y: m.b * p.x + m.d * p.y + m.f }; };
        const p0 = at(0), p1 = at(L);
        const inOuter = p => p.x > outer.l && p.x < outer.r && p.y > outer.t && p.y < outer.b;
        if (inOuter(p0) || inOuter(p1)) continue;               // terminates at the label — a leader, not a crossing
        const lineIdx = docIdx.get(s.el) ?? -1;
        const occluded = p => opaqueShapes.some(sh =>
          docIdx.get(sh.el) > lineIdx &&
          p.x > sh.r.left && p.x < sh.r.right && p.y > sh.r.top && p.y < sh.r.bottom);
        const step = Math.max(3, L / 400);                       // user units
        let hit = false;
        for (let u = step; u < L && !hit; u += step) {
          const p = at(u);
          if (p.x > inner.l && p.x < inner.r && p.y > inner.t && p.y < inner.b && !occluded(p)) hit = true;
        }
        if (hit) {
          push('warn', { svg: name, type: 'line-through-text',
            text: t.el.textContent.trim().slice(0, 40), el: s.tag,
            detail: 'route around (S4 §3 corridors) or halo the label (S4 paint-order stroke)' });
        }
      }
    }
    // 9. edge-manifest diff (S4 §9): the only deterministic check that catches
    // reversed and mis-routed arrows — they render fine and pass every
    // geometric check. Manifest = comment inside the svg (or immediately
    // before it): <!-- edges: FROM.port -> TO.port | ... -->, ports L/R/T/B.
    const manifestRaw = [];
    const walker = document.createTreeWalker(svg, NodeFilter.SHOW_COMMENT);
    while (walker.nextNode()) {
      const mm = walker.currentNode.nodeValue.match(/^\s*edges:\s*([\s\S]+)$/);
      if (mm) manifestRaw.push(mm[1]);
    }
    if (!manifestRaw.length) {                                   // fallback: comment just before the svg
      let n = svg.previousSibling, hops = 0;
      while (n && hops < 4) {
        if (n.nodeType === 8) {
          const mm = n.nodeValue.match(/^\s*edges:\s*([\s\S]+)$/);
          if (mm) { manifestRaw.push(mm[1]); }
          break;
        }
        if (n.nodeType === 1) break;
        n = n.previousSibling; hops++;
      }
    }
    const topoEdges = arrowEdges.filter(ed => !ed.legend);
    if (topoEdges.length && !manifestRaw.length) {
      push('warn', { svg: name, type: 'manifest-missing', arrows: topoEdges.length,
        detail: 'S4 §9: a figure with arrowed edges carries <!-- edges: FROM.port -> TO.port | ... --> so routing is mechanically auditable' });
    }
    if (manifestRaw.length) {
      const entries = [];
      for (const raw of manifestRaw) {
        for (const part of raw.split('|')) {
          const txt = part.trim();
          if (!txt) continue;
          const pm = txt.match(/^([\w-]+)\.([LRTBlrtb])\s*(?:→|->)\s*([\w-]+)\.([LRTBlrtb])$/);
          if (!pm) {
            // error, not warn: an unparsable entry silently disables the only
            // deterministic check for reversed/mis-routed arrows on that edge
            push('error', { svg: name, type: 'manifest-entry-unparsable', entry: txt.slice(0, 60),
              detail: 'expected exactly FROM.port -> TO.port with ports L/R/T/B - no annotations, no prose' });
            continue;
          }
          entries.push({ from: pm[1], fp: pm[2].toUpperCase(), to: pm[3], tp: pm[4].toUpperCase(), raw: txt });
        }
      }
      const shapes2d = all.filter(x => ['rect', 'circle', 'ellipse', 'polygon'].includes(x.tag));
      const resolve = nm => {                                    // id > data-name > exact-match label
        let el = null;
        for (const c of svg.querySelectorAll('[id]')) { if (c.id === nm) { el = c; break; } }
        if (!el) for (const c of svg.querySelectorAll('[data-name]')) {
          if (c.getAttribute('data-name') === nm) { el = c; break; }
        }
        if (el) return { r: el.getBoundingClientRect() };
        const cands = texts.filter(t => t.el.textContent.trim().toLowerCase() === nm.toLowerCase());
        if (cands.length > 1) return { ambiguous: true };
        if (cands.length === 1) {
          const t = cands[0];
          const tcx = (t.r.left + t.r.right) / 2, tcy = (t.r.top + t.r.bottom) / 2;
          let box = null;                                        // labeled-box idiom: smallest shape holding the label
          for (const sh of shapes2d) {
            const r = sh.r, a = r.width * r.height;
            if (a >= 0.9 * svgArea) continue;
            if (tcx > r.left && tcx < r.right && tcy > r.top && tcy < r.bottom) {
              if (!box || a < box.a) box = { r, a };
            }
          }
          return { r: box ? box.r : t.r };
        }
        return null;
      };
      const side = (r, p) =>
        p === 'L' ? { x1: r.left,  y1: r.top,    x2: r.left,  y2: r.bottom } :
        p === 'R' ? { x1: r.right, y1: r.top,    x2: r.right, y2: r.bottom } :
        p === 'T' ? { x1: r.left,  y1: r.top,    x2: r.right, y2: r.top } :
                    { x1: r.left,  y1: r.bottom, x2: r.right, y2: r.bottom };
      const segDist = (px, py, s) => {
        const dx = s.x2 - s.x1, dy = s.y2 - s.y1;
        const len2 = dx * dx + dy * dy || 1;
        let tt = ((px - s.x1) * dx + (py - s.y1) * dy) / len2;
        tt = Math.max(-0.06, Math.min(1.06, tt));                // small along-side slack
        return Math.hypot(px - (s.x1 + tt * dx), py - (s.y1 + tt * dy));
      };
      const resolved = [];
      const badNames = new Set();
      for (const e of entries) {
        const F = resolve(e.from), T = resolve(e.to);
        for (const [nm, R] of [[e.from, F], [e.to, T]]) {
          if (badNames.has(nm)) continue;
          if (!R) { badNames.add(nm);
            push('warn', { svg: name, type: 'manifest-name-unresolved', name: nm,
              detail: 'give the node an id / data-name, or a label whose exact text is the name' });
          } else if (R.ambiguous) { badNames.add(nm);
            push('warn', { svg: name, type: 'manifest-name-ambiguous', name: nm,
              detail: 'several labels carry this exact text — use an id or data-name' });
          }
        }
        if (F && T && !F.ambiguous && !T.ambiguous) resolved.push({ e, F, T });
      }
      // node-gap: manifest-resolved node boxes that touch or nearly touch make
      // ports degenerate — an edge starting on a shared border "belongs" to
      // both nodes, which is how a broken cycle can satisfy
      // a correct manifest. Routing needs a gutter (S4 §3).
      const nodeRects = [];
      const seenNR = new Set();
      for (const en of resolved) {
        for (const [nm, R] of [[en.e.from, en.F], [en.e.to, en.T]]) {
          const k = [R.r.left, R.r.top, R.r.right, R.r.bottom].map(v => Math.round(v)).join(',');
          if (!seenNR.has(k)) { seenNR.add(k); nodeRects.push({ nm, r: R.r }); }
        }
      }
      const seenGap = new Set();
      for (let i = 0; i < nodeRects.length; i++) {
        for (let j = i + 1; j < nodeRects.length; j++) {
          const a = nodeRects[i].r, b = nodeRects[j].r;
          const contains = (o, p) => o.left <= p.left && o.right >= p.right && o.top <= p.top && o.bottom >= p.bottom;
          if (contains(a, b) || contains(b, a)) continue;
          const gx = Math.max(a.left, b.left) - Math.min(a.right, b.right);
          const gy = Math.max(a.top, b.top) - Math.min(a.bottom, b.bottom);
          const gap = Math.max(gx, gy) / scale;
          const gk = [nodeRects[i].nm, nodeRects[j].nm].sort().join('|');
          if (gap < 6 && !seenGap.has(gk)) {
            seenGap.add(gk);
            push('warn', { svg: name, type: 'node-gap',
              nodes: nodeRects[i].nm + ' / ' + nodeRects[j].nm, gap_units: +gap.toFixed(1),
              detail: 'node boxes touch or sit < 6u apart: ports are ambiguous and edges have no routing corridor (S4 §3)' });
          }
        }
      }
      const TOL_TO = 9, TOL_FROM = 20;                           // land 2-4px short + estimate slop
      const pairs = [];
      resolved.forEach((en, ei) => topoEdges.forEach((ed, di) => {
        const dTo = segDist(ed.ex, ed.ey, side(en.T.r, en.e.tp)) / scale;
        const dFrom = segDist(ed.sx, ed.sy, side(en.F.r, en.e.fp)) / scale;
        if (dTo <= TOL_TO && dFrom <= TOL_FROM) pairs.push({ ei, di, score: dTo + dFrom });
      }));
      pairs.sort((a, b) => a.score - b.score);                   // optimal-first one-to-one matching
      const entryMatched = new Set(), edgeMatched = new Set();
      for (const p of pairs) {
        if (entryMatched.has(p.ei) || edgeMatched.has(p.di)) continue;
        entryMatched.add(p.ei); edgeMatched.add(p.di);
      }
      resolved.forEach((en, ei) => {
        if (entryMatched.has(ei)) return;
        let bestD = Infinity;
        for (const ed of topoEdges) {
          const d = segDist(ed.ex, ed.ey, side(en.T.r, en.e.tp)) / scale;
          if (d < bestD) bestD = d;
        }
        push('error', { svg: name, type: 'manifest-edge-mismatch', edge: en.e.raw,
          nearest_arrow_to_target_units: bestD === Infinity ? null : +bestD.toFixed(1),
          detail: 'no drawn marker-end edge lands on the declared TO port from the declared FROM side — reversed, mis-routed, or missing' });
      });
      topoEdges.forEach((ed, di) => {
        if (edgeMatched.has(di)) return;
        push('warn', { svg: name, type: 'edge-not-in-manifest',
          looks_like: nearestTarget(ed.sx, ed.sy, ed.el).lbl + ' -> ' + nearestTarget(ed.ex, ed.ey, ed.el).lbl,
          detail: 'add the edge to the manifest, or remove it from the drawing' });
      });
    }
  });
  return issues;
}
