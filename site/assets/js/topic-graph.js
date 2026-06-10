/* ICRA 2026 Topic Map — interactive topic graph.
 *
 * Self-contained Cytoscape.js widget. Expects, already loaded on the page:
 *   - cytoscape            (https://unpkg.com/cytoscape)
 *   - cytoscapeFcose       (https://unpkg.com/cytoscape-fcose) + its dep layout-base/cose-base
 * Data is fetched from window.TOPIC_DATA_BASE (default "./"):
 *   - topic_graph.json   {nodes:[{id,label,group,count,paperIds}], edges:[{source,target,weight}], meta}
 *   - topic_papers.json  {id:{title,abstract,authors,source,workshop,code,url,primary,topics}}
 *
 * Markup it expects on the page:
 *   <div id="tm-graph"></div>           graph canvas
 *   <div id="tm-panel"></div>           side panel (titles / abstracts)
 *   <input id="tm-search">              optional filter box
 *   <button id="tm-reset">              optional reset button
 */
(function () {
  "use strict";

  var BASE = (window.TOPIC_DATA_BASE || "./").replace(/\/?$/, "/");

  // Coarse super-category -> colour. 3Blue1Brown / Manim palette.
  var GROUP_COLORS = {
    "Estimation & Mapping": "#58C4DD",   // BLUE
    "Perception": "#5CD0B3",             // TEAL
    "Learning": "#F0AC5F",               // GOLD
    "Manipulation": "#FC6255",           // RED
    "Locomotion & Platforms": "#83C167", // GREEN
    "Planning & Control": "#E8C547",     // YELLOW
    "Applications": "#CF8DE5",           // PURPLE
    "Methods & Tooling": "#E07A9B",      // MAROON/PINK
  };
  var DEFAULT_COLOR = "#9CDCEB";
  var ACCENT = "#58C4DD"; // 3b1b signature blue

  function esc(s) {
    return (s == null ? "" : String(s)).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }

  function el(id) { return document.getElementById(id); }

  Promise.all([
    fetch(BASE + "topic_graph.json").then(function (r) { return r.json(); }),
    fetch(BASE + "topic_papers.json").then(function (r) { return r.json(); }),
  ]).then(function (res) {
    init(res[0], res[1]);
  }).catch(function (e) {
    var p = el("tm-panel");
    if (p) p.innerHTML = '<p class="tm-error">Failed to load topic data: ' + esc(e.message) + "</p>";
    // eslint-disable-next-line no-console
    console.error("topic-graph: data load failed", e);
  });

  function init(graph, papers) {
    if (window.cytoscapeFcose) { window.cytoscapeFcose(window.cytoscape); }

    var counts = graph.nodes.map(function (n) { return n.count; });
    var maxCount = Math.max.apply(null, counts);
    var maxWeight = Math.max.apply(null, graph.edges.map(function (e) { return e.weight; }).concat([1]));

    var elements = [];
    graph.nodes.forEach(function (n) {
      elements.push({ data: {
        id: n.id, label: n.label, group: n.group, count: n.count,
        paperIds: n.paperIds,
        color: GROUP_COLORS[n.group] || DEFAULT_COLOR,
        // node diameter 22..96 px, scaled by sqrt(count)
        size: 22 + 74 * Math.sqrt(n.count / maxCount),
      }});
    });
    graph.edges.forEach(function (e) {
      elements.push({ data: {
        id: e.source + "__" + e.target, source: e.source, target: e.target,
        weight: e.weight, width: 1 + 7 * (e.weight / maxWeight),
      }});
    });

    var cy = window.cytoscape({
      container: el("tm-graph"),
      elements: elements,
      wheelSensitivity: 0.2,
      style: [
        { selector: "node", style: {
          "background-color": "data(color)",
          "background-opacity": 0.96,
          "width": "data(size)", "height": "data(size)",
          "label": "data(label)",
          "font-size": 11, "font-weight": 600,
          "font-family": "\"Source Serif 4\", Charter, Georgia, serif",
          "color": "#eef4ff",
          "text-valign": "center", "text-halign": "center",
          "text-wrap": "wrap", "text-max-width": "data(size)",
          "text-outline-color": "#0a0c16", "text-outline-width": 2.6,
          // circular ring (no box); transparent until highlighted
          "border-width": 3, "border-color": "data(color)", "border-opacity": 0,
          "transition-property": "opacity border-opacity border-width",
          "transition-duration": "150ms",
        }},
        { selector: "edge", style: {
          "width": "data(width)", "line-color": "#39507a",
          "curve-style": "haystack", "haystack-radius": 0, "opacity": 0.5,
        }},
        { selector: "node:selected", style: {
          "border-width": 5, "border-color": ACCENT, "border-opacity": 1,
        }},
        { selector: "node.hl", style: {
          "border-width": 3, "border-color": ACCENT, "border-opacity": 0.85,
        }},
        { selector: "edge.hl", style: { "line-color": ACCENT, "opacity": 0.9 } },
        { selector: ".faded", style: { "opacity": 0.06, "text-opacity": 0.04 } },
        { selector: ".hl", style: { "opacity": 1, "text-opacity": 1 } },
      ],
      layout: window.cytoscapeFcose
        ? { name: "fcose", quality: "proof", nodeRepulsion: 9000,
            idealEdgeLength: function (e) { return 140 / Math.sqrt(e.data("weight")); },
            animate: false, padding: 30 }
        : { name: "cose", animate: false, padding: 30 },
    });

    // --- interactions -------------------------------------------------------
    function showTopic(node) {
      var d = node.data();
      var ids = (d.paperIds || []).slice();
      ids.sort(function (a, b) {
        return (papers[a] ? papers[a].title : a).localeCompare(papers[b] ? papers[b].title : b);
      });
      var html = '<div class="tm-topic-head" style="border-color:' + esc(d.color) + '">' +
        '<h3>' + esc(d.label) + "</h3>" +
        '<span class="tm-meta">' + esc(d.group) + " · " + d.count + " papers</span></div>" +
        '<ol class="tm-papers">';
      ids.forEach(function (pid) {
        var p = papers[pid] || { title: pid, abstract: "" };
        var badge = p.source === "workshop" ? "W" : "P";
        html += '<li class="tm-paper" data-pid="' + esc(pid) + '">' +
          '<span class="tm-badge tm-' + badge + '">' + badge + "</span>" +
          '<span class="tm-title">' + esc(p.title) + "</span>" +
          '<div class="tm-abstract" hidden></div></li>';
      });
      html += "</ol>";
      var panel = el("tm-panel");
      panel.innerHTML = html;
      panel.querySelectorAll(".tm-paper").forEach(function (li) {
        li.querySelector(".tm-title").addEventListener("click", function () {
          var pid = li.getAttribute("data-pid");
          var box = li.querySelector(".tm-abstract");
          if (!box.hidden) { box.hidden = true; return; }
          var p = papers[pid] || {};
          var meta = [];
          if (p.authors && p.authors.length) meta.push(esc(p.authors.slice(0, 8).join(", ")));
          // Proceedings paper id as recorded in the metadata (pp:0011 -> 0011).
          if (p.source === "proceedings" && pid.indexOf("pp:") === 0) {
            meta.push("Paper ID " + esc(pid.slice(3)));
          }
          if (p.workshop) meta.push("Workshop: " + esc(p.workshop));
          var links = [];
          if (p.url) links.push('<a href="' + esc(p.url) + '" target="_blank" rel="noopener">source</a>');
          if (p.code) links.push('<a href="' + esc(p.code) + '" target="_blank" rel="noopener">code</a>');
          box.innerHTML =
            (meta.length ? '<div class="tm-authors">' + meta.join(" — ") + "</div>" : "") +
            "<p>" + esc(p.abstract || "(no abstract)") + "</p>" +
            (links.length ? '<div class="tm-links">' + links.join(" · ") + "</div>" : "");
          box.hidden = false;
        });
      });
    }

    cy.on("tap", "node", function (evt) {
      var node = evt.target;
      cy.elements().addClass("faded").removeClass("hl");
      node.removeClass("faded").addClass("hl");
      node.neighborhood().removeClass("faded").addClass("hl");
      showTopic(node);
    });
    cy.on("tap", function (evt) {
      if (evt.target === cy) { cy.elements().removeClass("faded hl"); }
    });

    // --- search + reset -----------------------------------------------------
    var search = el("tm-search");
    if (search) {
      search.addEventListener("input", function () {
        var q = search.value.trim().toLowerCase();
        if (!q) { cy.elements().removeClass("faded hl"); return; }
        cy.elements().addClass("faded").removeClass("hl");
        var match = cy.nodes().filter(function (n) {
          return n.data("label").toLowerCase().indexOf(q) !== -1 ||
                 n.data("group").toLowerCase().indexOf(q) !== -1;
        });
        match.removeClass("faded").addClass("hl");
        match.connectedEdges().connectedNodes().removeClass("faded").addClass("hl");
      });
    }
    var reset = el("tm-reset");
    if (reset) {
      reset.addEventListener("click", function () {
        if (search) search.value = "";
        cy.elements().removeClass("faded hl");
        cy.fit(undefined, 30);
      });
    }

    // --- legend -------------------------------------------------------------
    var legend = el("tm-legend");
    if (legend) {
      legend.innerHTML = Object.keys(GROUP_COLORS).map(function (g) {
        return '<span class="tm-leg"><i style="background:' + GROUP_COLORS[g] + '"></i>' + esc(g) + "</span>";
      }).join("");
    }

    var intro = el("tm-panel");
    if (intro && !intro.innerHTML.trim()) {
      intro.innerHTML = '<p class="tm-hint">Click a topic to list its papers (' +
        graph.meta.papers + ' papers across ' + graph.nodes.length +
        ' topics). Click a paper title to read its abstract.</p>';
    }
  }
})();
