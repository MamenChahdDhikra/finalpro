"""
TP N°3 — Logique modale (USTHB, Master 1 SII, 2025-2026)
Modélisation d'un modèle modal M = <W, R, V> à 6 mondes.

Contexte (NOUVEAU, différent du TD) :
  Un réseau de 6 nœuds IoT (capteurs S1…S6) surveille un entrepôt.
  Propositions : f (feu), m (fumée), a (alarme), e (évacuation).

Le graphe d'accessibilité est dense (plusieurs arêtes croisées),
contrairement au petit exemple à 2 mondes de l'exercice 5 du TD.
"""

# ============================================================
#  MODÈLE MODAL — 6 MONDES, GRAPHE RICHE
# ============================================================

W = {"w1", "w2", "w3", "w4", "w5", "w6"}

# Relation R : chaque monde a plusieurs successeurs (graphe non trivial)
R = {
    "w1": {"w1", "w2", "w3", "w4"},
    "w2": {"w2", "w3", "w5"},
    "w3": {"w1", "w4", "w6"},
    "w4": {"w4", "w5", "w6"},
    "w5": {"w2", "w5", "w6"},
    "w6": {"w3", "w4", "w6"},
}

# Valuation V — états des capteurs par nœud
V = {
    "f": {"w1", "w3", "w5"},           # feu détecté
    # NB: on retire m de w3 pour obtenir en w1 : (<>f & <>m) vrai mais <>(f&m) faux
    "m": {"w2", "w4", "w6"},           # fumée
    "a": {"w1", "w2", "w4", "w5"},     # alarme sonore
    "e": {"w3", "w5", "w6"},           # ordre d'évacuation
}


# ============================================================
#  ÉVALUATEUR MODAL
# ============================================================

def evaluate(formula, world, W, R, V):
    op = formula[0]

    if op == "atom":
        return world in V.get(formula[1], set())

    if op == "not":
        return not evaluate(formula[1], world, W, R, V)

    if op == "and":
        return evaluate(formula[1], world, W, R, V) and evaluate(
            formula[2], world, W, R, V
        )

    if op == "or":
        return evaluate(formula[1], world, W, R, V) or evaluate(
            formula[2], world, W, R, V
        )

    if op == "imp":
        return (not evaluate(formula[1], world, W, R, V)) or evaluate(
            formula[2], world, W, R, V
        )

    if op == "box":
        accessible = R.get(world, set())
        if not accessible:
            return True
        return all(evaluate(formula[1], w2, W, R, V) for w2 in accessible)

    if op == "dia":
        accessible = R.get(world, set())
        if not accessible:
            return False
        return any(evaluate(formula[1], w2, W, R, V) for w2 in accessible)

    raise ValueError(f"Opérateur inconnu: {op}")


def formula_to_str(formula):
    op = formula[0]
    if op == "atom":
        return formula[1]
    if op == "not":
        return f"~{formula_to_str(formula[1])}"
    if op == "and":
        return f"({formula_to_str(formula[1])} & {formula_to_str(formula[2])})"
    if op == "or":
        return f"({formula_to_str(formula[1])} | {formula_to_str(formula[2])})"
    if op == "imp":
        return f"({formula_to_str(formula[1])} -> {formula_to_str(formula[2])})"
    if op == "box":
        return f"[] {formula_to_str(formula[1])}"
    if op == "dia":
        return f"<> {formula_to_str(formula[1])}"
    return "?"


# ============================================================
#  PROPRIÉTÉS DE R
# ============================================================

def is_reflexive(W, R):
    return all(w in R.get(w, set()) for w in W)


def is_symmetric(W, R):
    for w in W:
        for v in R.get(w, set()):
            if w not in R.get(v, set()):
                return False
    return True


def is_transitive(W, R):
    for w in W:
        for v in R.get(w, set()):
            for u in R.get(v, set()):
                if u not in R.get(w, set()):
                    return False
    return True


def is_serial(W, R):
    return all(len(R.get(w, set())) > 0 for w in W)


def is_euclidean(W, R):
    for w in W:
        acc = R.get(w, set())
        for v in acc:
            for u in acc:
                if u not in R.get(v, set()):
                    return False
    return True


def satisfying_worlds(formula, W, R, V):
    return {w for w in W if evaluate(formula, w, W, R, V)}


def is_valid(formula, W, R, V):
    return satisfying_worlds(formula, W, R, V) == W


def count_edges(R):
    return sum(len(R.get(w, set())) for w in R)


# ============================================================
#  AFFICHAGE
# ============================================================

def print_graph_ascii(W, R, V):
    print("=" * 70)
    print("  GRAPHE DU MODELE (6 mondes, relation R dense)")
    print("=" * 70)
    print("""
        w1 -----> w2 -----> w5
         | \\       | \\       | \\
         |  \\      |  \\      |  \\
         v   \\     v   \\     v   \\
        w3 --> w4 --> w6 <------+
         |      | \\      ^
         +------+  \\-----+
              (aretes croisees : w3->w1, w6->w3, w5->w2, ...)
    """)
    print(f"  Nombre d'aretes orientees |R| = {count_edges(R)}")
    print()
    for w in sorted(W):
        targets = ", ".join(sorted(R.get(w, set())))
        props = sorted(p for p, worlds in V.items() if w in worlds)
        props_str = ", ".join(props) if props else "(aucune)"
        print(f"    [{w}]  R -> {{{targets}}}   |   Vrai : {props_str}")
    print()


def show_gui(W, R, V):
    """
    Affiche une interface graphique (tkinter) pour rendre le graphe plus clair.
    On dessine :
      - 6 noeuds w1..w6
      - les fleches selon la relation R
      - les propositions vraies V(w)
    """
    try:
        import tkinter as tk
        from math import cos, sin, pi
    except Exception as e:
        print("GUI non disponible (tkinter manquant). Erreur:", e)
        return

    # Coordonnees (cercle autour du centre)
    nodes = sorted(W)
    cx, cy = 400, 350
    radius = 220

    positions = {}
    for i, w in enumerate(nodes):
        angle = 2 * pi * i / len(nodes) - pi / 2
        x = cx + radius * cos(angle)
        y = cy + radius * sin(angle)
        positions[w] = (x, y)

    # Conversion simple pour afficher V en texte (sans caracteres speciaux)
    prop_label = {
        "f": "f",
        "m": "m",
        "a": "a",
        "e": "e",
    }

    root = tk.Tk()
    root.title("Modele modal M - Visualisation (6 mondes)")
    root.geometry("860x760")

    canvas = tk.Canvas(root, width=860, height=700, bg="white")
    canvas.pack()

    # Dessin des fleches (arcs)
    for w in nodes:
        x1, y1 = positions[w]
        for v in sorted(R.get(w, set())):
            x2, y2 = positions[v]
            canvas.create_line(
                x1,
                y1,
                x2,
                y2,
                fill="gray",
                width=1,
                arrow=tk.LAST,
                arrowshape=(10, 12, 4),
            )

    # Dessin des noeuds
    for w in nodes:
        x, y = positions[w]
        canvas.create_oval(x - 18, y - 18, x + 18, y + 18, fill="#cfe8ff", outline="blue", width=2)
        canvas.create_text(x, y, text=w, font=("Arial", 12, "bold"))

        props = sorted([p for p, worlds in V.items() if w in worlds])
        props_disp = ", ".join(prop_label.get(p, p) for p in props) if props else "none"
        canvas.create_text(
            x,
            y + 34,
            text=f"V: {props_disp}",
            font=("Arial", 9),
            fill="black",
        )

    # L'aide utilisateur
    canvas.create_text(
        20,
        20,
        anchor="nw",
        text="Relation R (fleches) + valuation V (V: propositions vraies). Fermer la fenetre pour terminer.",
        font=("Arial", 10),
        fill="black",
    )

    root.mainloop()


def export_graph_html(W, R, V, out_path="model_modal_graph.html", open_in_browser=True):
    """
    Exporte une interface web (HTML + Canvas + JS) pour visualiser :
      - Les noeuds w1..w6
      - Les fleches selon la relation R
      - La valuation V (quelles propositions sont vraies dans chaque monde)
    Optionnellement, ouvre le fichier dans le navigateur.
    """
    import json
    import os

    W_list = sorted(W)
    # R compact: objet { "w1": ["w1","w2",...], ... }
    R_obj = {w: sorted(list(R.get(w, set()))) for w in W_list}
    V_obj = {p: sorted(list(V.get(p, set()))) for p in sorted(V)}

    # Valuation par monde (pour affichage)
    V_by_world = {w: [] for w in W_list}
    for prop, worlds in V_obj.items():
        for w in worlds:
            V_by_world[w].append(prop)
    V_by_world = {w: sorted(vs) for w, vs in V_by_world.items()}

    prop_display = {"f": "f", "m": "m", "a": "a", "e": "e"}

    data = {
        "W": W_list,
        "R": R_obj,
        "V_by_world": V_by_world,
        "prop_display": prop_display,
    }

    html = f"""<!doctype html>
<html lang="fr">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Modele modal M - Visualisation</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 16px; }}
    #wrap {{ display: flex; gap: 16px; align-items: flex-start; flex-wrap: wrap; }}
    #panel {{ width: 340px; }}
    canvas {{ border: 1px solid #ddd; background: #fff; }}
    .btnrow {{ margin-top: 8px; }}
    button {{ padding: 8px 10px; margin-right: 8px; }}
    code {{ background: #f5f5f5; padding: 2px 6px; border-radius: 4px; }}
  </style>
</head>
<body>
  <h2>Modele modal M = &lt;W, R, V&gt; (6 mondes)</h2>
  <div id="wrap">
    <div>
      <canvas id="c" width="920" height="700"></canvas>
    </div>
    <div id="panel">
      <div><b>Interaction</b></div>
      <div style="margin-top:6px;">
        Cliquez sur un noeud <code>w_i</code> pour mettre en evidence les fleches sortantes.
      </div>
      <div class="btnrow">
        <button onclick="selectNode(null)">Reset</button>
      </div>
      <hr/>
      <div><b>Etat courant</b></div>
      <div id="info" style="margin-top:8px; line-height:1.5;">Aucun noeud selectionne.</div>
    </div>
  </div>

<script>
  const data = {json.dumps(data, ensure_ascii=False)};
  const W = data.W;
  const R = data.R;
  const V_by_world = data.V_by_world;
  const prop_display = data.prop_display;

  const canvas = document.getElementById('c');
  const ctx = canvas.getContext('2d');

  const cx = 460, cy = 350, radius = 230;
  const nodeR = 20;
  let selected = null;

  // positions autour d'un cercle
  const pos = {{}};
  for (let i = 0; i < W.length; i++) {{
    const angle = 2 * Math.PI * i / W.length - Math.PI/2;
    pos[W[i]] = {{ x: cx + radius * Math.cos(angle), y: cy + radius * Math.sin(angle) }};
  }}

  function drawArrow(x1, y1, x2, y2, color, width=1) {{
    const head = 10;
    const angle = Math.atan2(y2 - y1, x2 - x1);
    ctx.strokeStyle = color;
    ctx.fillStyle = color;
    ctx.lineWidth = width;
    ctx.beginPath();
    ctx.moveTo(x1, y1);
    ctx.lineTo(x2, y2);
    ctx.stroke();

    const hx = x2 - head * Math.cos(angle);
    const hy = y2 - head * Math.sin(angle);
    ctx.beginPath();
    ctx.moveTo(x2, y2);
    ctx.lineTo(hx + 4 * Math.cos(angle + Math.PI/2), hy + 4 * Math.sin(angle + Math.PI/2));
    ctx.lineTo(hx + 4 * Math.cos(angle - Math.PI/2), hy + 4 * Math.sin(angle - Math.PI/2));
    ctx.closePath();
    ctx.fill();
  }}

  function propsText(w) {{
    const props = V_by_world[w] || [];
    if (props.length === 0) return 'none';
    return props.map(p => prop_display[p] || p).join(', ');
  }}

  function setInfo() {{
    const el = document.getElementById('info');
    if (!selected) {{
      el.innerHTML = 'Aucun noeud selectionne.';
      return;
    }}
    const succ = R[selected] || [];
    el.innerHTML = `Selection : <b>${{selected}}</b><br/>
      Successeurs accessibles : <b>${{succ.join(', ')}}</b><br/>
      V(${{
        selected
      }}) = <b>${{propsText(selected)}}</b>`;
  }}

  function clear() {{
    ctx.clearRect(0, 0, canvas.width, canvas.height);
  }}

  function render() {{
    clear();

    // Fleches
    for (const src of W) {{
      const edges = R[src] || [];
      for (const dst of edges) {{
        const a = pos[src];
        const b = pos[dst];
        // Decale debut/fin pour que l'arrow commence/termine sur le bord du cercle
        const dx = b.x - a.x;
        const dy = b.y - a.y;
        const len = Math.sqrt(dx*dx + dy*dy) || 1;
        const sx = a.x + (dx/len) * nodeR;
        const sy = a.y + (dy/len) * nodeR;
        const ex = b.x - (dx/len) * nodeR;
        const ey = b.y - (dy/len) * nodeR;

        const active = (selected === null) ? false : (selected === src);
        const color = active ? '#d33' : '#999';
        const width = active ? 2.2 : 1;
        drawArrow(sx, sy, ex, ey, color, width);
      }}
    }}

    // Noeuds
    for (const w of W) {{
      const p = pos[w];
      const isSel = (selected === w);
      ctx.fillStyle = isSel ? '#ffd37a' : '#cfe8ff';
      ctx.strokeStyle = isSel ? '#b46a00' : '#1f66b2';
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.arc(p.x, p.y, nodeR, 0, 2*Math.PI);
      ctx.fill();
      ctx.stroke();

      ctx.fillStyle = '#000';
      ctx.font = '16px Arial';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillText(w, p.x, p.y);

      // Texte valuation sous le noeud
      ctx.font = '12px Arial';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'top';
      ctx.fillText('V: ' + propsText(w), p.x, p.y + nodeR + 8);
    }}

    setInfo();
  }}

  function selectNode(w) {{
    selected = w;
    render();
  }}

  // Detecter click sur un noeud
  canvas.addEventListener('click', (ev) => {{
    const rect = canvas.getBoundingClientRect();
    const x = (ev.clientX - rect.left) * (canvas.width / rect.width);
    const y = (ev.clientY - rect.top) * (canvas.height / rect.height);
    let best = null;
    let bestDist = Infinity;
    for (const w of W) {{
      const p = pos[w];
      const dx = x - p.x;
      const dy = y - p.y;
      const dist = Math.sqrt(dx*dx + dy*dy);
      if (dist <= nodeR + 6 && dist < bestDist) {{
        best = w;
        bestDist = dist;
      }}
    }}
    selectNode(best);
  }});

  render();
</script>
</body>
</html>"""

    abs_out = os.path.abspath(out_path)
    with open(abs_out, "w", encoding="utf-8") as f:
        f.write(html)

    if open_in_browser:
        try:
            import webbrowser

            webbrowser.open("file://" + abs_out)
        except Exception as e:
            print("Impossible d'ouvrir le navigateur automatiquement. Fichier:", abs_out, "Erreur:", e)
    print("Interface HTML generee:", abs_out)


def print_model(W, R, V):
    print("=" * 70)
    print("  MODÈLE M = <W, R, V>  —  Réseau IoT (6 capteurs)")
    print("=" * 70)
    print(f"  W = {sorted(W)}")
    print(f"  Propositions : f=feu, m=fumée, a=alarme, e=évacuation\n")
    print("  R (accessibilité) :")
    for w in sorted(W):
        print(f"    {w} R {{ {', '.join(sorted(R[w]))} }}")
    print("\n  V :")
    for prop in sorted(V):
        print(f"    V({prop}) = {sorted(V[prop])}")
    print()


def print_properties(W, R):
    print("=" * 70)
    print("  PROPRIÉTÉS DE R")
    print("=" * 70)
    checks = [
        ("Réflexive", is_reflexive(W, R)),
        ("Symétrique", is_symmetric(W, R)),
        ("Transitive", is_transitive(W, R)),
        ("Sérielle", is_serial(W, R)),
        ("Euclidienne", is_euclidean(W, R)),
    ]
    for name, ok in checks:
        print(f"  {'[OUI]' if ok else '[NON]'}  {name}")
    print()


def justify(world, formula, W, R, V):
    fstr = formula_to_str(formula)
    val = evaluate(formula, world, W, R, V)
    mark = "VRAIE" if val else "FAUSSE"
    print(f"\n  M,{world} |= {fstr}  ?  => {mark}")
    print(f"  Justification :")

    if formula[0] == "atom":
        print(f"    {formula[1]} ∈ V ?  {world in V.get(formula[1], set())}")

    elif formula[0] == "not":
        sub_val = evaluate(formula[1], world, W, R, V)
        print(f"    ~ : {formula_to_str(formula[1])} est {'V' if sub_val else 'F'} en {world}")
        print(f"    => ~ est {'F' if sub_val else 'V'}")

    elif formula[0] in ("and", "or", "imp"):
        v1 = evaluate(formula[1], world, W, R, V)
        v2 = evaluate(formula[2], world, W, R, V)
        print(f"    {formula_to_str(formula[1])} : {'V' if v1 else 'F'}")
        print(f"    {formula_to_str(formula[2])} : {'V' if v2 else 'F'}")

    elif formula[0] == "box":
        acc = sorted(R.get(world, set()))
        sub = formula[1]
        print(f"    []phi : phi doit etre V dans TOUS les mondes accessibles depuis {world}")
        print(f"    Succ({world}) = {acc}")
        for w2 in acc:
            v2 = evaluate(sub, w2, W, R, V)
            print(f"      {formula_to_str(sub)} en {w2} : {'V' if v2 else 'F'}")

    elif formula[0] == "dia":
        acc = sorted(R.get(world, set()))
        sub = formula[1]
        print(f"    <>phi : phi doit etre V dans AU MOINS UN monde accessible depuis {world}")
        print(f"    Succ({world}) = {acc}")
        for w2 in acc:
            v2 = evaluate(sub, w2, W, R, V)
            print(f"      {formula_to_str(sub)} en {w2} : {'V' if v2 else 'F'}")


def print_assertions(assertions, W, R, V):
    print("=" * 70)
    print("  ASSERTIONS À VÉRIFIER (style TD Exercice 2, nouveau contenu)")
    print("=" * 70)
    for world, formula in assertions:
        justify(world, formula, W, R, V)


def print_exercise5_demo(W, R, V):
    """Démo type Ex.5 TD : ◊p∧◊q vrai mais ◊(p∧q) faux (en w1)."""
    f = ("atom", "f")
    m = ("atom", "m")
    w = "w1"
    f1 = ("and", ("dia", f), ("dia", m))
    f2 = ("dia", ("and", f, m))

    print("=" * 70)
    print("  DÉMONSTRATION (Exercice 5 TD) — sur 6 mondes, pas seulement 2")
    print("=" * 70)
    print(f"  En {w} : on veut <>f & <>m VRAI et <>(f&m) FAUX\n")
    justify(w, f1, W, R, V)
    justify(w, f2, W, R, V)
    print("""
  Interpretation :
    <>f et <>m peuvent etre vrais separement (fumee possible ici,
    feu possible ailleurs) sans qu'il existe un monde accessible
    ou les DEUX sont vrais simultanement.
    => La conjonction modale <>(f&m) est plus forte que (<>f & <>m).
""")


def print_evaluation_table(formulas, W, R, V):
    print("=" * 70)
    print("  TABLE D'ÉVALUATION")
    print("=" * 70)
    worlds = sorted(W)
    header = f"  {'Formule':<28}" + "".join(f"{w:>6}" for w in worlds)
    print(header)
    print("  " + "-" * (len(header) - 2))
    for f in formulas:
        row = f"  {formula_to_str(f):<28}"
        for w in worlds:
            row += ("  V  " if evaluate(f, w, W, R, V) else "  F  ")
        print(row)
    print()


def print_validity(formulas, W, R, V):
    print("=" * 70)
    print("  VALIDITÉ DANS M (formule vraie dans tous les mondes ?)")
    print("=" * 70)
    for f, comment in formulas:
        sat = satisfying_worlds(f, W, R, V)
        valid = sat == W
        status = "VALIDE dans M" if valid else f"vraie en {sorted(sat)} seulement"
        print(f"  {formula_to_str(f)}")
        print(f"    => {status}")
        if comment:
            print(f"    => {comment}")
    print()


def print_epistemic_note():
    print("=" * 70)
    print("  INTERPRÉTATION ÉPISTÉMIQUE")
    print("=" * 70)
    print("""
  Chaque monde w_i = état d'information du superviseur depuis le capteur i.
  w_j accessible depuis w_i  =>  scénario encore jugé possible par i.

  []phi  : le superviseur sait phi (phi dans tous les scenarios possibles)
  <>phi  : le superviseur considere phi possible (phi dans au moins un scenario)

  Exemple : []a en w4 => l'alarme est connue/certaine depuis tous les
  etats accessibles depuis w4 (w4, w5, w6 ont tous a vrai).
""")


# ============================================================
#  MAIN
# ============================================================

def main():
    f, m, a, e = ("atom", "f"), ("atom", "m"), ("atom", "a"), ("atom", "e")

    print("\n" + "=" * 70)
    print("  TP N°3 — LOGIQUE MODALE")
    print("  USTHB Master 1 SII — Représentation et raisonnement")
    print("  Exemple original : 6 mondes, graphe dense (entrepôt IoT)")
    print("=" * 70 + "\n")

    print_graph_ascii(W, R, V)
    print_model(W, R, V)
    print_properties(W, R)

    assertions = [
        ("w1", ("box", ("imp", f, m))),           # □(f→m)
        ("w2", ("not", ("box", a))),              # ¬□a
        ("w3", ("dia", ("and", f, e))),           # ◊(f∧e)
        ("w4", ("box", a)),                       # □a
        ("w5", ("imp", ("dia", f), ("box", e))),   # ◊f → □e
        ("w6", ("not", ("dia", ("box", ("not", m))))),  # ¬◊□¬m
    ]
    print_assertions(assertions, W, R, V)

    print_exercise5_demo(W, R, V)

    key_formulas = [
        f, m, a, e,
        ("box", f),
        ("dia", m),
        ("and", ("dia", f), ("dia", m)),
        ("dia", ("and", f, m)),
        ("box", ("or", a, e)),
        ("imp", ("box", f), f),
        ("or", f, ("not", f)),
    ]
    print_evaluation_table(key_formulas, W, R, V)

    validity_check = [
        (("imp", ("box", f), f), "Axiome T (nécessite R réflexive)"),
        (("imp", ("dia", f), ("box", ("dia", f))), "Axiome 5 / euclidien"),
        (("or", a, ("not", a)), "Tiers exclu propositionnel"),
        (("and", ("dia", f), ("dia", ("not", f))), "Satisfiable, non valide"),
    ]
    print_validity(validity_check, W, R, V)
    print_epistemic_note()

    print("=" * 70)
    print("  FIN DU TP")
    print("=" * 70)

    # Interface graphique (plus de dessin) via HTML + Canvas (souvent plus fiable que tkinter)
    export_graph_html(W, R, V, out_path="model_modal_graph.html", open_in_browser=True)

    # Si tu veux vraiment une fenetre tkinter aussi, debloque cette ligne.
    # show_gui(W, R, V)


if __name__ == "__main__":
    main()
