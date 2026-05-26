"""
TP N°4 — Logique des défauts (USTHB, Master 1 SII, 2025-2026)

Contexte NOUVEAU (different du TD) :
  Gestion d'un parc de vehicules autonomes dans une zone industrielle.
  Le TD utilise champignons, chretiens libanais, A/B/C, etc.
  Ici : robots r1..r6, zones, missions, maintenance, securite.

Moteur Python pur : theories <W,D>, calcul des extensions (Reiter),
verification de coherence, export HTML interactif.

Usage :
  python tp4_default_logic.py
"""

from __future__ import annotations

import json
import os
import webbrowser
from dataclasses import dataclass, field
from typing import Dict, FrozenSet, List, Optional, Set, Tuple

# ---------------------------------------------------------------------------
#  Formules propositionnelles (AST minimal)
# ---------------------------------------------------------------------------

Formula = Tuple  # ('atom', name) | ('not', f) | ('and', f, g) | ('or', f, g) | ('imp', f, g)


def atom(name: str) -> Formula:
    return ("atom", name)


def neg(f: Formula) -> Formula:
    return ("not", f)


def _and(f: Formula, g: Formula) -> Formula:
    return ("and", f, g)


def _or(f: Formula, g: Formula) -> Formula:
    return ("or", f, g)


def imp(f: Formula, g: Formula) -> Formula:
    return ("imp", f, g)


def formula_to_str(f: Formula) -> str:
    op = f[0]
    if op == "atom":
        return f[1]
    if op == "not":
        return f"~{formula_to_str(f[1])}"
    if op == "and":
        return f"({formula_to_str(f[1])} & {formula_to_str(f[2])})"
    if op == "or":
        return f"({formula_to_str(f[1])} | {formula_to_str(f[2])})"
    if op == "imp":
        return f"({formula_to_str(f[1])} -> {formula_to_str(f[2])})"
    return "?"


def literals_in_formula(f: Formula) -> Set[str]:
    """Retourne les noms d'atomes presents."""
    op = f[0]
    if op == "atom":
        return {f[1]}
    if op == "not":
        return literals_in_formula(f[1])
    return literals_in_formula(f[1]) | literals_in_formula(f[2])


# ---------------------------------------------------------------------------
#  Theorie des defauts
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Default:
    """Regle de defaut : prerequis : justification / conclusion."""

    name: str
    prereq: Optional[Formula]  # None = vrai (regle sans prerequis)
    justification: Tuple[Formula, ...]
    conclusion: Formula

    def signature(self) -> str:
        pre = formula_to_str(self.prereq) if self.prereq else "T"
        just = " & ".join(formula_to_str(j) for j in self.justification)
        return f"{self.name}: {pre} : {just} / {formula_to_str(self.conclusion)}"


@dataclass
class DefaultTheory:
    """Delta = <W, D>."""

    name: str
    W: Tuple[Formula, ...]
    D: Tuple[Default, ...]
    description: str = ""


# ---------------------------------------------------------------------------
#  Moteur : cloture + coherence + extensions
# ---------------------------------------------------------------------------


def literal_key(name: str, positive: bool) -> str:
    return name if positive else f"~{name}"


def parse_literal(key: str) -> Tuple[str, bool]:
    if key.startswith("~"):
        return key[1:], False
    return key, True


class KnowledgeBase:
    """Ensemble de faits (litteraux) + implications fermees par propagation."""

    def __init__(self, atoms: Set[str]):
        self.atoms = atoms
        self.positive: Set[str] = set()
        self.negative: Set[str] = set()
        self.implications: List[Tuple[Formula, Formula]] = []

    def copy(self) -> "KnowledgeBase":
        kb = KnowledgeBase(self.atoms)
        kb.positive = set(self.positive)
        kb.negative = set(self.negative)
        kb.implications = list(self.implications)
        return kb

    def set_literal(self, name: str, value: bool) -> bool:
        if value:
            if name in self.negative:
                return False
            self.positive.add(name)
        else:
            if name in self.positive:
                return False
            self.negative.add(name)
        return True

    def has_atom(self, name: str) -> Optional[bool]:
        if name in self.positive:
            return True
        if name in self.negative:
            return False
        return None

    def add_formula(self, f: Formula) -> bool:
        op = f[0]
        if op == "atom":
            return self.set_literal(f[1], True)
        if op == "not":
            inner = f[1]
            if inner[0] != "atom":
                self.implications.append((f, atom("_dummy")))
                return True
            return self.set_literal(inner[1], False)
        if op == "imp":
            self.implications.append((f[1], f[2]))
            return True
        if op == "and":
            return self.add_formula(f[1]) and self.add_formula(f[2])
        if op == "or":
            ok1 = self.add_formula(f[1])
            ok2 = self.add_formula(f[2])
            return ok1 or ok2
        return True

    def eval_formula(self, f: Formula) -> Optional[bool]:
        op = f[0]
        if op == "atom":
            return self.has_atom(f[1])
        if op == "not":
            v = self.eval_formula(f[1])
            if v is None:
                return None
            return not v
        if op == "and":
            v1, v2 = self.eval_formula(f[1]), self.eval_formula(f[2])
            if v1 is False or v2 is False:
                return False
            if v1 is True and v2 is True:
                return True
            return None
        if op == "or":
            v1, v2 = self.eval_formula(f[1]), self.eval_formula(f[2])
            if v1 is True or v2 is True:
                return True
            if v1 is False and v2 is False:
                return False
            return None
        if op == "imp":
            v1, v2 = self.eval_formula(f[1]), self.eval_formula(f[2])
            if v1 is False:
                return True
            if v1 is True and v2 is False:
                return False
            if v1 is True and v2 is True:
                return True
            return None
        return None

    def close(self) -> bool:
        changed = True
        while changed:
            changed = False
            for ant, cons in self.implications:
                va = self.eval_formula(ant)
                if va is True:
                    vc = self.eval_formula(cons)
                    if vc is False:
                        return False
                    if vc is None:
                        if cons[0] == "atom":
                            if not self.set_literal(cons[1], True):
                                return False
                            changed = True
                        elif cons[0] == "not" and cons[1][0] == "atom":
                            if not self.set_literal(cons[1][1], False):
                                return False
                            changed = True
        return True

    def is_consistent(self) -> bool:
        kb = self.copy()
        return kb.close()

    def literals(self) -> FrozenSet[str]:
        out = set()
        for a in self.positive:
            out.add(literal_key(a, True))
        for a in self.negative:
            out.add(literal_key(a, False))
        return frozenset(out)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, KnowledgeBase):
            return False
        return self.literals() == other.literals()

    def __hash__(self) -> int:
        return hash(self.literals())


def kb_from_theory(W: Tuple[Formula, ...], atoms: Set[str]) -> KnowledgeBase:
    kb = KnowledgeBase(atoms)
    for f in W:
        if not kb.add_formula(f):
            kb.close()
            break
    kb.close()
    return kb


def default_applicable(d: Default, kb: KnowledgeBase) -> bool:
    if d.prereq is not None:
        v = kb.eval_formula(d.prereq)
        if v is not True:
            return False
    for j in d.justification:
        vj = kb.eval_formula(j)
        if vj is False:
            return False
    test = kb.copy()
    for j in d.justification:
        if not test.add_formula(j):
            return False
    if not test.add_formula(d.conclusion):
        return False
    return test.close()


def apply_default(d: Default, kb: KnowledgeBase) -> Optional[KnowledgeBase]:
    if not default_applicable(d, kb):
        return None
    new_kb = kb.copy()
    for j in d.justification:
        new_kb.add_formula(j)
    if not new_kb.add_formula(d.conclusion):
        return None
    if not new_kb.close():
        return None
    return new_kb


def kb_entails(kb: KnowledgeBase, f: Formula) -> bool:
    v = kb.eval_formula(f)
    if v is True:
        return True
    if v is False:
        return False
    test = kb.copy()
    if f[0] == "atom":
        test.set_literal(f[1], False)
    elif f[0] == "not" and f[1][0] == "atom":
        test.set_literal(f[1][1], True)
    else:
        return False
    return not test.close()


def compute_extension_raw(
    theory: DefaultTheory, atoms: Set[str], applied: Tuple[int, ...] = ()
) -> Optional[KnowledgeBase]:
    """Applique uniquement les defauts listes (sans fermeture greedy)."""
    kb = kb_from_theory(theory.W, atoms)
    for idx in applied:
        nkb = apply_default(theory.D[idx], kb)
        if nkb is None:
            return None
        kb = nkb
    return kb if kb.is_consistent() else None


def is_maximal_extension(theory: DefaultTheory, kb: KnowledgeBase, applied: Tuple[int, ...]) -> bool:
    applied_set = set(applied)
    for i, d in enumerate(theory.D):
        if i in applied_set:
            continue
        if default_applicable(d, kb):
            return False
    return True


def find_all_extensions(theory: DefaultTheory) -> List[Tuple[KnowledgeBase, Tuple[int, ...]]]:
    """Recherche backtracking de toutes les extensions maximales."""
    atoms: Set[str] = set()
    for f in theory.W:
        atoms |= literals_in_formula(f)
    for d in theory.D:
        for part in (d.prereq, d.conclusion, *d.justification):
            if part:
                atoms |= literals_in_formula(part)

    n = len(theory.D)
    extensions: Dict[FrozenSet[str], Tuple[int, ...]] = {}

    def backtrack(applied: Tuple[int, ...]):
        kb = compute_extension_raw(theory, atoms, applied)
        if kb is None:
            return
        lit = kb.literals()
        applied_set = set(applied)

        applicable = [
            i
            for i in range(n)
            if i not in applied_set and default_applicable(theory.D[i], kb)
        ]

        if not applicable:
            if is_maximal_extension(theory, kb, applied):
                if lit not in extensions:
                    extensions[lit] = applied
            return

        for i in applicable:
            backtrack(applied + (i,))

    backtrack(())
    return [(kb_from_literals(lit, atoms), ext) for lit, ext in extensions.items()]


def kb_from_literals(lit: FrozenSet[str], atoms: Set[str]) -> KnowledgeBase:
    kb = KnowledgeBase(atoms)
    for key in lit:
        name, pos = parse_literal(key)
        kb.set_literal(name, pos)
    kb.close()
    return kb


# ---------------------------------------------------------------------------
#  THEORIE PRINCIPALE — Parc de robots autonomes (6 robots, 12 defauts)
# ---------------------------------------------------------------------------

# Atomes (noms courts)
# robot Ri, zone Z, mission M, maintenance X, etc.

R1, R2, R3, R4, R5, R6 = "r1", "r2", "r3", "r4", "r5", "r6"
DELIV = "delivery"
PATROL = "patrol"
INSPECT = "inspect"
ZONE_A = "zoneA"
SLOW = "slow"
PKG = "package"
CAM = "camera"
BAT_LOW = "battery_low"
CHARGE = "charging"
MAINT = "maintenance"
ALERT = "alert"
BLOCKED = "blocked"
PRIORITY = "priority_route"

THEORY_FLEET = DefaultTheory(
    name="Parc_robots_industriels",
    description=(
        "Six robots autonomes (r1..r6) operent dans une usine. "
        "W contient des faits certains ; D encode des regles par defaut "
        "(comportement habituel + exceptions)."
    ),
    W=(
        atom(R1),
        atom(R2),
        atom(R3),
        atom(R4),
        atom(R5),
        atom(R6),
        atom(DELIV),
        atom(ZONE_A),
        imp(atom(R1), atom(DELIV)),
        imp(atom(R2), atom(PATROL)),
        imp(atom(R3), atom(INSPECT)),
        imp(atom(R4), atom(DELIV)),
        imp(atom(R5), atom(PATROL)),
        imp(atom(R6), atom(INSPECT)),
        atom(BAT_LOW),
        imp(atom(R3), atom(BAT_LOW)),
        imp(atom(R6), atom(BAT_LOW)),
        neg(atom(MAINT)),
    ),
    D=(
        Default(
            "d1",
            imp(atom(R1), atom(DELIV)),
            (neg(atom(MAINT)),),
            atom(PKG),
        ),
        Default(
            "d2",
            imp(atom(R4), atom(DELIV)),
            (neg(atom(MAINT)),),
            atom(PKG),
        ),
        Default(
            "d3",
            imp(atom(R2), atom(PATROL)),
            (neg(atom(BLOCKED)),),
            atom(CAM),
        ),
        Default(
            "d5",
            imp(atom(R5), atom(PATROL)),
            (neg(atom(BLOCKED)),),
            atom(CAM),
        ),
        Default(
            "d4",
            atom(ZONE_A),
            (neg(atom(MAINT)),),
            atom(SLOW),
        ),
        Default(
            "d6",
            None,
            (atom(BAT_LOW),),
            atom(CHARGE),
        ),
        Default(
            "d7",
            atom(BAT_LOW),
            (neg(atom(CHARGE)),),
            atom(ALERT),
        ),
        Default(
            "d8",
            imp(atom(R3), atom(INSPECT)),
            (neg(atom(PKG)),),
            atom(CAM),
        ),
        Default(
            "d9",
            imp(atom(R6), atom(INSPECT)),
            (neg(atom(PKG)),),
            atom(CAM),
        ),
        Default(
            "d10",
            atom(PRIORITY),
            (neg(atom(SLOW)),),
            atom(ALERT),
        ),
        Default(
            "d11",
            None,
            (neg(atom(ALERT)),),
            atom(PRIORITY),
        ),
        Default(
            "d12",
            atom(SLOW),
            (neg(atom(PRIORITY)),),
            atom(BLOCKED),
        ),
        # Conflit potentiel : alert vs priorite (extensions multiples)
    ),
)


# ---------------------------------------------------------------------------
#  Petite theorie de demo (validation rapide, pas le TD)
# ---------------------------------------------------------------------------

THEORY_DEMO = DefaultTheory(
    name="Demo_independante",
    description="Petite theorie agricole (pas le TD champignons) pour test rapide.",
    W=(atom("solar"), atom("farm")),
    D=(
        Default("x1", atom("solar"), (neg(atom("rain")),), atom("dry_soil")),
        Default("x2", atom("dry_soil"), (neg(atom("flood")),), atom("irrigate")),
        Default("x3", None, (neg(atom("manual_off")),), neg(atom("irrigate"))),
    ),
)


# ---------------------------------------------------------------------------
#  Affichage console
# ---------------------------------------------------------------------------


def print_theory(theory: DefaultTheory):
    print("=" * 72)
    print(f"  THEORIE : {theory.name}")
    print("=" * 72)
    if theory.description:
        print(f"  {theory.description}\n")
    print("  W (faits certains) :")
    for f in theory.W:
        print(f"    - {formula_to_str(f)}")
    print(f"\n  D ({len(theory.D)} regles de defaut) :")
    for d in theory.D:
        print(f"    - {d.signature()}")
    print()


def print_extension(idx: int, kb: KnowledgeBase, applied: Tuple[int, ...], theory: DefaultTheory):
    print(f"  --- Extension E{idx} ---")
    names = [theory.D[i].name for i in applied]
    print(f"  Defauts appliques ({len(applied)}) : {', '.join(names) if names else '(aucun)'}")
    pos = sorted(kb.positive)
    neg = sorted(kb.negative)
    print(f"  Litteraux positifs ({len(pos)}) : {', '.join(pos) if pos else '(aucun)'}")
    print(f"  Litteraux negatifs ({len(neg)}) : {', '.join(f'~{x}' for x in neg) if neg else '(aucun)'}")
    queries = [
        ("package sur r1 ?", atom(PKG)),
        ("camera sur r2 ?", atom(CAM)),
        ("slow en zone A ?", atom(SLOW)),
        ("charging ?", atom(CHARGE)),
        ("alert ?", atom(ALERT)),
    ]
    print("  Consequences interrogees :")
    for label, q in queries:
        v = kb.eval_formula(q)
        txt = "VRAI" if v is True else ("FAUX" if v is False else "INCONNU")
        print(f"    {label} => {txt}")
    print()


def print_all_extensions(theory: DefaultTheory):
    print("=" * 72)
    print(f"  EXTENSIONS de {theory.name}")
    print("=" * 72)
    exts = find_all_extensions(theory)
    if not exts:
        print("  Aucune extension trouvee.\n")
        return exts
    print(f"  Nombre d'extensions : {len(exts)}\n")
    for i, (kb, applied) in enumerate(exts, 1):
        print_extension(i, kb, applied, theory)
    return exts


def compare_theories():
    print("=" * 72)
    print("  COMPARAISON non-monotone (W vs W') — contexte robots")
    print("=" * 72)
    w_prime = tuple(f for f in THEORY_FLEET.W if f != neg(atom(MAINT))) + (atom(MAINT),)
    theory_prime = DefaultTheory(
        name="Parc_avec_maintenance",
        description="On remplace ~maintenance par maintenance : d1,d2,d4 ne s'appliquent plus.",
        W=w_prime,
        D=THEORY_FLEET.D,
    )
    e1 = find_all_extensions(THEORY_FLEET)
    e2 = find_all_extensions(theory_prime)
    print(f"  Sans maintenance : {len(e1)} extension(s)")
    print(f"  Avec maintenance : {len(e2)} extension(s)")
    for i, (kb, _) in enumerate(e1, 1):
        pkg = kb.eval_formula(atom(PKG))
        print(f"    E{i} (sans maint.) : package = {pkg}")
    for i, (kb, _) in enumerate(e2, 1):
        pkg = kb.eval_formula(atom(PKG))
        print(f"    E{i} (avec maint.)  : package = {pkg}")
    print()


# ---------------------------------------------------------------------------
#  Export HTML interactif
# ---------------------------------------------------------------------------


def export_html(theory: DefaultTheory, exts, out_path: str = "default_logic_tp4.html"):
    defaults_data = [
        {
            "name": d.name,
            "sig": d.signature(),
            "pre": formula_to_str(d.prereq) if d.prereq else "T",
            "just": [formula_to_str(j) for j in d.justification],
            "conc": formula_to_str(d.conclusion),
        }
        for d in theory.D
    ]
    w_data = [formula_to_str(f) for f in theory.W]
    ext_data = []
    for i, (kb, applied) in enumerate(exts, 1):
        ext_data.append(
            {
                "id": i,
                "applied": list(applied),
                "positive": sorted(kb.positive),
                "negative": sorted(kb.negative),
            }
        )

    payload = {
        "theory_name": theory.name,
        "description": theory.description,
        "W": w_data,
        "defaults": defaults_data,
        "extensions": ext_data,
    }

    html = f"""<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="utf-8"/>
  <title>TP4 - Logique des defauts</title>
  <style>
    body {{ font-family: Segoe UI, Arial, sans-serif; margin: 20px; background: #f4f6f8; }}
    h1 {{ color: #1a365d; }}
    .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }}
    .card {{ background: #fff; border-radius: 8px; padding: 16px; box-shadow: 0 2px 8px rgba(0,0,0,.08); }}
    .card h3 {{ margin-top: 0; color: #2c5282; }}
    ul {{ line-height: 1.6; }}
    .def {{ border-left: 4px solid #3182ce; padding-left: 10px; margin: 8px 0; }}
    .ext {{ border-left: 4px solid #38a169; padding-left: 10px; margin: 10px 0; }}
    .tag {{ display: inline-block; background: #bee3f8; padding: 2px 8px; border-radius: 4px; margin: 2px; font-size: 12px; }}
    .tag.neg {{ background: #fed7d7; }}
    select {{ padding: 8px; font-size: 14px; }}
  </style>
</head>
<body>
  <h1>TP4 - Logique des defauts</h1>
  <p id="desc"></p>
  <div class="grid">
    <div class="card">
      <h3>W — Faits certains</h3>
      <ul id="wlist"></ul>
    </div>
    <div class="card">
      <h3>D — Regles de defaut ({len(theory.D)})</h3>
      <div id="dlist"></div>
    </div>
  </div>
  <div class="card" style="margin-top:16px;">
    <h3>Extensions calculees</h3>
    <label>Choisir une extension : </label>
    <select id="extsel"></select>
    <div id="extdetail" style="margin-top:12px;"></div>
  </div>
<script>
const data = {json.dumps(payload, ensure_ascii=False)};
document.getElementById('desc').textContent = data.description;
const wul = document.getElementById('wlist');
data.W.forEach(w => {{ const li = document.createElement('li'); li.textContent = w; wul.appendChild(li); }});
const dl = document.getElementById('dlist');
data.defaults.forEach(d => {{
  const div = document.createElement('div');
  div.className = 'def';
  div.innerHTML = '<b>' + d.name + '</b><br/><code>' + d.sig + '</code>';
  dl.appendChild(div);
}});
const sel = document.getElementById('extsel');
data.extensions.forEach(e => {{
  const o = document.createElement('option');
  o.value = e.id;
  o.textContent = 'Extension E' + e.id + ' (defauts: ' + (e.applied.join(', ') || 'aucun') + ')';
  sel.appendChild(o);
}});
function showExt() {{
  const id = parseInt(sel.value);
  const e = data.extensions.find(x => x.id === id);
  const box = document.getElementById('extdetail');
  let html = '<div class="ext"><b>Defauts appliques :</b> ' + (e.applied.join(', ') || 'aucun') + '<br/>';
  html += '<b>Positifs :</b> ';
  e.positive.forEach(p => html += '<span class="tag">'+p+'</span>');
  html += '<br/><b>Negatifs :</b> ';
  e.negative.forEach(n => html += '<span class="tag neg">~'+n+'</span>');
  html += '</div>';
  box.innerHTML = html;
}}
sel.addEventListener('change', showExt);
if (data.extensions.length) showExt();
</script>
</body>
</html>"""

    path = os.path.abspath(out_path)
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    try:
        webbrowser.open("file://" + path)
    except OSError:
        pass
    print(f"  Interface HTML : {path}")
    return path


# ---------------------------------------------------------------------------
#  Main
# ---------------------------------------------------------------------------


def main():
    print("\n" + "=" * 72)
    print("  TP N°4 — LOGIQUE DES DEFAUTS")
    print("  USTHB Master 1 SII — Representation et raisonnement")
    print("  Exemple original : parc de 6 robots autonomes (grand modele)")
    print("=" * 72 + "\n")

    print_theory(THEORY_DEMO)
    print_all_extensions(THEORY_DEMO)

    print_theory(THEORY_FLEET)
    exts = print_all_extensions(THEORY_FLEET)
    compare_theories()

    print("=" * 72)
    print("  SYNTHESE")
    print("=" * 72)
    print(f"""
  Theorie principale : {len(THEORY_FLEET.W)} formules dans W,
  {len(THEORY_FLEET.D)} regles de defaut, 6 robots (r1..r6).

  Interpretation :
    - Les robots de livraison ont normalement un colis (d1, d2)
      sauf si maintenance.
    - Patrol / inspect activent camera par defaut.
    - zoneA => slow ; battery_low => charging ; etc.

  Non-monotonie : ajouter maintenance a W peut invalider package
  (8 extensions -> 2 extensions dans l'exemple calcule).

  Outils du TP (Java/online) : tweetyproject.org, defaultlogic, etc.
  Ce script Python reproduit le raisonnement sans dependance externe.
""")
    print("=" * 72)
    print("  FIN DU TP4")
    print("=" * 72)

    if exts:
        export_html(THEORY_FLEET, exts)


if __name__ == "__main__":
    main()
