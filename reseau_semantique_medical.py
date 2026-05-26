"""
=============================================================================
TP 5 – Réseaux Sémantiques : Propagation de Marqueurs, Héritage & Exceptions
=============================================================================

Master 1 SII – Module : Représentation et Raisonnement
Année Universitaire : 2025-2026

EXEMPLE CHOISI : Domaine de la Médecine et des Maladies Infectieuses
─────────────────────────────────────────────────────────────────────
Un réseau sémantique riche modélisant :
  • La hiérarchie des maladies infectieuses
  • Les agents pathogènes (bactéries, virus, parasites, champignons)
  • Les traitements (antibiotiques, antiviraux, antiparasitaires…)
  • Les modes de transmission (aérien, contact, vectoriel, alimentaire…)
  • Des exceptions (résistances, cas atypiques)
  • Des modalités (croyances, souhaits de différents acteurs)
  • Des instances concrètes (COVID-19, Tuberculose, Paludisme…)
=============================================================================
"""

from collections import defaultdict, deque
from typing import Optional


# ═══════════════════════════════════════════════════════════════════════════
#  SECTION 1 – STRUCTURE DE DONNÉES : Le Réseau Sémantique
# ═══════════════════════════════════════════════════════════════════════════

class Node:
    """
    Représente un nœud dans le réseau sémantique.
    
    Attributs
    ---------
    name        : identifiant unique du nœud
    node_type   : 'concept' | 'instance' | 'property' | 'action' | 'modal'
    properties  : dictionnaire {propriété: valeur} directement attachées au nœud
    exceptions  : ensemble de propriétés que ce nœud N'hérite PAS
    """

    def __init__(self, name: str, node_type: str = "concept"):
        self.name = name
        self.node_type = node_type
        self.properties: dict = {}
        self.exceptions: set = set()   # propriétés bloquées (liens d'exception)

    def add_property(self, prop: str, value):
        self.properties[prop] = value

    def add_exception(self, prop: str):
        """Déclare que cette propriété ne doit PAS être héritée (lien d'exception)."""
        self.exceptions.add(prop)

    def __repr__(self):
        return f"Node({self.name!r}, type={self.node_type!r})"


class SemanticNetwork:
    """
    Réseau Sémantique complet avec :
      - Nœuds typés
      - Liens orientés étiquetés
      - Propagation de marqueurs (Partie 1)
      - Héritage avec saturation (Partie 2)
      - Inhibition des exceptions (Partie 3)
    """

    # ── Types de liens reconnus ──────────────────────────────────────────
    LINK_ISA          = "is-a"           # instance → classe
    LINK_AKO          = "a-kind-of"      # sous-classe → sur-classe
    LINK_HAS          = "has"            # possession / propriété
    LINK_CAUSES       = "causes"         # causalité
    LINK_TREATS       = "treats"         # traitement
    LINK_TRANSMITS    = "transmitted-by" # mode de transmission
    LINK_PRODUCED_BY  = "produced-by"    # produit par
    LINK_PART_OF      = "part-of"        # composition
    LINK_DISTINCT     = "distinct-from"  # distinction
    LINK_BELIEVES     = "believes"       # modalité épistémique
    LINK_WANTS        = "wants"          # modalité déontique
    LINK_KNOWS        = "knows"          # modalité épistémique forte
    LINK_EXCEPTION    = "exception"      # lien d'exception (inhibition)
    LINK_TYPICALLY    = "typically"      # lien par défaut (défeasible)

    def __init__(self, name: str = "Réseau Sémantique Médical"):
        self.name = name
        self.nodes: dict[str, Node] = {}
        # adjacence : {source: [(target, link_type, weight, is_default)]
        self.edges: dict[str, list] = defaultdict(list)
        # index inverse pour navigation montante
        self.reverse_edges: dict[str, list] = defaultdict(list)

    # ── Construction ────────────────────────────────────────────────────

    def add_node(self, name: str, node_type: str = "concept", **props) -> Node:
        if name not in self.nodes:
            self.nodes[name] = Node(name, node_type)
        node = self.nodes[name]
        for k, v in props.items():
            node.add_property(k, v)
        return node

    def add_edge(self, source: str, target: str,
                 link_type: str, is_default: bool = False,
                 is_exception: bool = False):
        """
        Ajoute un lien orienté source → target.
        
        is_default   : lien 'typiquement' (peut être annulé par exception)
        is_exception : lien bloquant la propagation sur une propriété
        """
        # s'assurer que les nœuds existent
        for n in (source, target):
            if n not in self.nodes:
                self.add_node(n)

        entry = (target, link_type, is_default, is_exception)
        if entry not in self.edges[source]:
            self.edges[source].append(entry)
            self.reverse_edges[target].append((source, link_type, is_default, is_exception))

        if is_exception:
            self.nodes[source].add_exception(link_type)

    # ── Affichage ────────────────────────────────────────────────────────

    def display(self):
        print(f"\n{'═'*65}")
        print(f"  RÉSEAU SÉMANTIQUE : {self.name}")
        print(f"{'═'*65}")
        print(f"  Nœuds  ({len(self.nodes)}) : {', '.join(sorted(self.nodes.keys()))}")
        print(f"  Liens  ({sum(len(v) for v in self.edges.values())}) :")
        for src in sorted(self.edges.keys()):
            for (tgt, ltype, is_def, is_exc) in self.edges[src]:
                marker = " [DEFAULT]" if is_def else (" [EXCEPTION]" if is_exc else "")
                print(f"    {src:35s} ──[{ltype}]──▶  {tgt}{marker}")
        print(f"{'═'*65}\n")

    # ───────────────────────────────────────────────────────────────────────
    #  PARTIE 1 – PROPAGATION DE MARQUEURS
    # ───────────────────────────────────────────────────────────────────────

    def marker_propagation(self,
                           start_nodes: list[str],
                           target_relation: str,
                           direction: str = "forward",
                           verbose: bool = True) -> list[str]:
        """
        Propagation de marqueurs depuis plusieurs nœuds sources,
        en suivant un type de relation donné.

        Paramètres
        ----------
        start_nodes       : liste de nœuds de départ (marqués initialement)
        target_relation   : type de lien à suivre
        direction         : 'forward'  → suit les arcs sortants
                            'backward' → remonte les arcs entrants
        verbose           : affiche la trace de propagation

        Retourne
        --------
        Liste des nœuds atteints (hors nœuds de départ).
        """
        if verbose:
            print(f"\n{'─'*60}")
            print(f"  PROPAGATION DE MARQUEURS")
            print(f"  Relation ciblée : [{target_relation}]")
            print(f"  Nœuds de départ : {start_nodes}")
            print(f"  Direction       : {direction}")
            print(f"{'─'*60}")

        visited: set[str] = set()
        queue: deque[tuple[str, int]] = deque()
        results: list[str] = []
        trace: list[str] = []   # pour l'affichage pédagogique

        for s in start_nodes:
            if s in self.nodes:
                queue.append((s, 0))
                visited.add(s)

        graph = self.edges if direction == "forward" else self.reverse_edges

        while queue:
            current, depth = queue.popleft()
            indent = "  " + "  " * depth

            if verbose:
                marker = "★" if current in start_nodes else "◆"
                print(f"{indent}{marker} {current}  (profondeur {depth})")

            neighbours = graph.get(current, [])
            for (neighbour, ltype, is_def, is_exc) in neighbours:
                if ltype != target_relation:
                    continue
                if is_exc:
                    if verbose:
                        print(f"{indent}  ✗ {neighbour}  [BLOQUÉ – lien d'exception]")
                    continue
                if neighbour not in visited:
                    visited.add(neighbour)
                    queue.append((neighbour, depth + 1))
                    if neighbour not in start_nodes:
                        results.append(neighbour)
                        trace.append(
                            f"{current} ──[{ltype}{'(défaut)' if is_def else ''}]──▶ {neighbour}"
                        )
                        if verbose:
                            print(f"{indent}  → {neighbour}  ({'défaut' if is_def else 'strict'})")

        if verbose:
            print(f"\n  ✅ Résultats trouvés ({len(results)}) :")
            if results:
                for r in results:
                    print(f"     • {r}")
            else:
                print("     (aucun résultat — manque de connaissances)")
            print(f"{'─'*60}\n")

        return results

    # ───────────────────────────────────────────────────────────────────────
    #  PARTIE 2 – HÉRITAGE ET SATURATION DU RÉSEAU
    # ───────────────────────────────────────────────────────────────────────

    def _get_ancestors(self, node_name: str) -> list[str]:
        """
        Remonte la hiérarchie (is-a + a-kind-of) pour obtenir tous les ancêtres,
        du plus proche au plus éloigné (BFS).
        """
        ancestors = []
        visited = {node_name}
        queue = deque([node_name])
        hierarchy_links = {self.LINK_ISA, self.LINK_AKO}

        while queue:
            current = queue.popleft()
            for (tgt, ltype, _, _) in self.edges.get(current, []):
                if ltype in hierarchy_links and tgt not in visited:
                    visited.add(tgt)
                    ancestors.append(tgt)
                    queue.append(tgt)
        return ancestors

    def inherit_properties(self, node_name: str,
                           respect_exceptions: bool = True,
                           verbose: bool = True) -> dict:
        """
        Calcule TOUTES les propriétés héritées par un nœud donné.

        Les propriétés propres du nœud ont priorité sur les propriétés héritées.
        Les liens d'exception bloquent l'héritage de certaines propriétés.
        Les liens 'typiquement' sont indiqués comme défauts (peuvent être écrasés).

        Paramètres
        ----------
        node_name          : nœud cible
        respect_exceptions : si True, les exceptions bloquent la propagation
        verbose            : trace détaillée

        Retourne
        --------
        Dictionnaire {propriété: (valeur, source, is_default)}
        """
        if node_name not in self.nodes:
            print(f"  ⚠ Nœud '{node_name}' introuvable.")
            return {}

        if verbose:
            print(f"\n{'─'*60}")
            print(f"  HÉRITAGE DE PROPRIÉTÉS  →  nœud : « {node_name} »")
            print(f"  Respect des exceptions : {respect_exceptions}")
            print(f"{'─'*60}")

        node = self.nodes[node_name]
        # propriétés finales : {prop: (valeur, source, is_default)}
        inherited: dict[str, tuple] = {}

        # 1) Propriétés directes du nœud (priorité maximale)
        for prop, val in node.properties.items():
            inherited[prop] = (val, node_name, False)
            if verbose:
                print(f"  [DIRECT]   {prop:30s} = {val}  (source: {node_name})")

        # Exceptions déclarées sur ce nœud
        blocked_props: set[str] = set(node.exceptions) if respect_exceptions else set()

        # 2) Parcours des ancêtres du plus proche au plus lointain
        ancestors = self._get_ancestors(node_name)
        if verbose and ancestors:
            print(f"\n  Ancêtres (ordre BFS) : {ancestors}")

        for ancestor in ancestors:
            anc_node = self.nodes[ancestor]
            for prop, val in anc_node.properties.items():
                if prop in blocked_props:
                    if verbose:
                        print(f"  [BLOQUÉ]   {prop:30s} (exception déclarée sur {node_name})")
                    continue
                if prop not in inherited:
                    is_def = prop in getattr(anc_node, "_default_props", set())
                    inherited[prop] = (val, ancestor, is_def)
                    if verbose:
                        tag = "[DÉFAUT]" if is_def else "[HÉRITÉ]"
                        print(f"  {tag:10s} {prop:30s} = {val}  (source: {ancestor})")
                else:
                    if verbose:
                        print(f"  [IGNORÉ]   {prop:30s} = {val}  "
                              f"(écrasé par {inherited[prop][1]})")

        if verbose:
            print(f"\n  → {len(inherited)} propriété(s) totale(s) pour '{node_name}'")
            print(f"{'─'*60}\n")

        return inherited

    def saturate(self, verbose: bool = True) -> int:
        """
        Sature le réseau : infère toutes les propriétés pour tous les nœuds
        et ajoute les liens manquants (clôture transitive de l'héritage).

        Retourne le nombre de nouveaux faits inférés.
        """
        if verbose:
            print(f"\n{'═'*60}")
            print("  SATURATION DU RÉSEAU (inférence totale)")
            print(f"{'═'*60}")

        new_facts = 0
        for node_name in list(self.nodes.keys()):
            inherited = self.inherit_properties(node_name,
                                                respect_exceptions=True,
                                                verbose=False)
            node = self.nodes[node_name]
            for prop, (val, source, is_def) in inherited.items():
                if prop not in node.properties:
                    node.properties[prop] = val
                    new_facts += 1
                    if verbose:
                        tag = "(défaut)" if is_def else ""
                        print(f"  INFÉRÉ : {node_name}.{prop} = {val}  "
                              f"← {source} {tag}")

        if verbose:
            print(f"\n  Total nouveaux faits inférés : {new_facts}")
            print(f"{'═'*60}\n")

        return new_facts

    # ───────────────────────────────────────────────────────────────────────
    #  PARTIE 3 – INHIBITION DES EXCEPTIONS
    # ───────────────────────────────────────────────────────────────────────

    def propagate_with_exception_inhibition(self,
                                            start_node: str,
                                            relation: str,
                                            verbose: bool = True) -> list[str]:
        """
        Propagation de marqueurs avec inhibition active des liens d'exception.

        Pour chaque nœud visité, on vérifie s'il a déclaré une exception sur
        la relation en cours ; si oui, la propagation est stoppée sur ce chemin.

        Paramètres
        ----------
        start_node : nœud de départ
        relation   : relation à suivre

        Retourne
        --------
        Liste des nœuds atteignables en respectant les exceptions.
        """
        if verbose:
            print(f"\n{'─'*60}")
            print(f"  PROPAGATION AVEC INHIBITION DES EXCEPTIONS")
            print(f"  Départ : {start_node}  |  Relation : [{relation}]")
            print(f"{'─'*60}")

        visited: set[str] = set()
        queue: deque[tuple[str, int]] = deque([(start_node, 0)])
        visited.add(start_node)
        results: list[str] = []

        while queue:
            current, depth = queue.popleft()
            node = self.nodes.get(current)
            indent = "  " + "  " * depth

            if verbose:
                print(f"{indent}◆ {current}")

            for (tgt, ltype, is_def, is_exc) in self.edges.get(current, []):
                if ltype != relation:
                    continue

                tgt_node = self.nodes.get(tgt)

                # Vérification de l'exception sur le nœud cible
                if tgt_node and relation in tgt_node.exceptions:
                    if verbose:
                        print(f"{indent}  ✗ {tgt}  "
                              f"[INHIBÉ – {tgt} a une exception sur '{relation}']")
                    continue

                # Vérification de l'exception sur le lien lui-même
                if is_exc:
                    if verbose:
                        print(f"{indent}  ✗ {tgt}  [INHIBÉ – lien marqué exception]")
                    continue

                if tgt not in visited:
                    visited.add(tgt)
                    queue.append((tgt, depth + 1))
                    if tgt != start_node:
                        results.append(tgt)
                        if verbose:
                            tag = " (défaut)" if is_def else ""
                            print(f"{indent}  ✔ {tgt}{tag}")

        if verbose:
            print(f"\n  ✅ Nœuds atteignables ({len(results)}) :")
            for r in results:
                print(f"     • {r}")
            print(f"{'─'*60}\n")

        return results


# ═══════════════════════════════════════════════════════════════════════════
#  SECTION 2 – CONSTRUCTION DU RÉSEAU MÉDICAL
# ═══════════════════════════════════════════════════════════════════════════

def build_medical_network() -> SemanticNetwork:
    """
    Construit un réseau sémantique riche modélisant le domaine médical :
    maladies infectieuses, agents pathogènes, traitements, transmissions.

    Connaissances encodées
    ──────────────────────
    HIÉRARCHIE DES MALADIES
    K01  Les maladies infectieuses sont des maladies.
    K02  Les maladies virales et les maladies bactériennes sont des maladies infectieuses.
    K03  Les maladies parasitaires et les maladies fongiques sont des maladies infectieuses.
    K04  Les maladies chroniques et les maladies aiguës sont des maladies.

    AGENTS PATHOGÈNES
    K05  Les virus, les bactéries, les parasites et les champignons sont des agents pathogènes.
    K06  Les agents pathogènes provoquent des maladies infectieuses.
    K07  Les bactéries sont des procaryotes unicellulaires.
    K08  Les virus sont des agents acellulaires dépourvus de métabolisme propre.
    K09  Les parasites sont des eucaryotes qui dépendent d'un hôte.

    TRAITEMENTS
    K10  Les antibiotiques traitent les maladies bactériennes.
    K11  Les antiviraux traitent les maladies virales.
    K12  Les antiparasitaires traitent les maladies parasitaires.
    K13  Les antifongiques traitent les maladies fongiques.
    K14  En général, les maladies infectieuses répondent à un traitement antimicrobien.
    K15  Les vaccins préviennent certaines maladies virales et bactériennes.

    TRANSMISSIONS
    K16  Les maladies respiratoires se transmettent par voie aérienne.
    K17  Les maladies vectorielles se transmettent par vecteur.
    K18  Les maladies entériques se transmettent par voie fécale-orale.
    K19  Les maladies sexuellement transmissibles se transmettent par contact direct.

    SYMPTÔMES ET EFFETS
    K20  Les maladies infectieuses provoquent de la fièvre.
    K21  Les maladies respiratoires provoquent une détresse respiratoire.
    K22  Les maladies neurologiques infectieuses provoquent des convulsions.

    INSTANCES CONCRÈTES
    K23  La COVID-19 est une maladie virale respiratoire.
    K24  La tuberculose est une maladie bactérienne respiratoire.
    K25  Le paludisme est une maladie parasitaire vectorielle.
    K26  La méningite bactérienne est une maladie bactérienne neurologique infectieuse.
    K27  La grippe est une maladie virale respiratoire.
    K28  Le choléra est une maladie bactérienne entérique.
    K29  La candidose est une maladie fongique.
    K30  Le VIH est une maladie virale sexuellement transmissible.

    EXCEPTIONS
    K31  La bactérie BMR (Bactérie Multi-Résistante) est une bactérie ;
         EXCEPTION : elle n'est PAS traitée par les antibiotiques (résistance).
    K32  Le botulisme est une maladie bactérienne ;
         EXCEPTION : il ne provoque PAS de fièvre (toxine, pas d'infection classique).
    K33  Typiquement les maladies bactériennes provoquent de la fièvre,
         mais le botulisme fait exception.

    LIENS PAR DÉFAUT
    K34  En général, les maladies infectieuses nécessitent une hospitalisation.
    K35  Les maladies chroniques n'induisent PAS une résolution spontanée.

    MODALITÉS (croyances / vouloir)
    K36  L'OMS sait que la COVID-19 est une maladie respiratoire.
    K37  Les climato-sceptiques ne croient pas que la pollution aggrave les maladies.
    K38  Les chercheurs en virologie croient que les antiviraux traitent la COVID-19.
    K39  Les gouvernements veulent que les vaccins préviennent les épidémies.
    """

    rs = SemanticNetwork("Réseau Médical – Maladies Infectieuses")

    # ── Concepts principaux ──────────────────────────────────────────────
    rs.add_node("maladie",                    node_type="concept")
    rs.add_node("maladie_infectieuse",        node_type="concept",
                provoque="fièvre",
                necessite="hospitalisation",   # défaut K34
                repond_a="traitement_antimicrobien")   # défaut K14
    rs.add_node("maladie_virale",             node_type="concept")
    rs.add_node("maladie_bacterienne",        node_type="concept",
                provoque="fièvre")
    rs.add_node("maladie_parasitaire",        node_type="concept")
    rs.add_node("maladie_fongique",           node_type="concept")
    rs.add_node("maladie_chronique",          node_type="concept",
                resolution_spontanee=False)
    rs.add_node("maladie_aigue",              node_type="concept")
    rs.add_node("maladie_respiratoire",       node_type="concept",
                provoque="détresse_respiratoire",
                transmission="voie_aérienne")
    rs.add_node("maladie_vectorielle",        node_type="concept",
                transmission="vecteur")
    rs.add_node("maladie_enterique",          node_type="concept",
                transmission="voie_fécale-orale")
    rs.add_node("maladie_sexuellement_transmissible", node_type="concept",
                transmission="contact_direct")
    rs.add_node("maladie_neurologique_infectieuse",  node_type="concept",
                provoque="convulsions")

    # ── Agents pathogènes ────────────────────────────────────────────────
    rs.add_node("agent_pathogene",            node_type="concept")
    rs.add_node("virus",                      node_type="concept",
                structure="acellulaire",
                metabolisme=False)
    rs.add_node("bacterie",                   node_type="concept",
                structure="procaryote_unicellulaire")
    rs.add_node("parasite",                   node_type="concept",
                structure="eucaryote",
                dependance="hote")
    rs.add_node("champignon",                 node_type="concept",
                structure="eucaryote")

    # ── Traitements ──────────────────────────────────────────────────────
    rs.add_node("antibiotique",               node_type="concept",
                type_traitement="antimicrobien")
    rs.add_node("antiviral",                  node_type="concept",
                type_traitement="antimicrobien")
    rs.add_node("antiparasitaire",            node_type="concept",
                type_traitement="antimicrobien")
    rs.add_node("antifongique",               node_type="concept",
                type_traitement="antimicrobien")
    rs.add_node("vaccin",                     node_type="concept",
                mode="prophylactique")
    rs.add_node("traitement_antimicrobien",   node_type="concept")

    # ── Instances de maladies ────────────────────────────────────────────
    rs.add_node("COVID-19",                   node_type="instance",
                agent="SARS-CoV-2",
                annee_emergence=2019)
    rs.add_node("tuberculose",                node_type="instance",
                agent="Mycobacterium_tuberculosis",
                duree="chronique")
    rs.add_node("paludisme",                  node_type="instance",
                agent="Plasmodium",
                vecteur="moustique_anophele")
    rs.add_node("meningite_bacterienne",      node_type="instance",
                agent="Neisseria_meningitidis")
    rs.add_node("grippe",                     node_type="instance",
                agent="Influenzavirus")
    rs.add_node("cholera",                    node_type="instance",
                agent="Vibrio_cholerae")
    rs.add_node("candidose",                  node_type="instance",
                agent="Candida_albicans")
    rs.add_node("VIH",                        node_type="instance",
                agent="HIV",
                chronique=True)
    rs.add_node("botulisme",                  node_type="instance",
                agent="Clostridium_botulinum",
                mecanisme="toxine")
    rs.add_node("bacterie_BMR",               node_type="instance",
                description="bactérie multi-résistante")

    # ── Acteurs modaux ───────────────────────────────────────────────────
    rs.add_node("OMS",                        node_type="modal")
    rs.add_node("climato_sceptiques",         node_type="modal")
    rs.add_node("chercheurs_en_virologie",    node_type="modal")
    rs.add_node("gouvernements",              node_type="modal")

    # ════════════════════════════════════════════════════════════════════
    #  LIENS DE LA HIÉRARCHIE
    # ════════════════════════════════════════════════════════════════════

    # Hiérarchie des maladies
    rs.add_edge("maladie_infectieuse",   "maladie",               SemanticNetwork.LINK_AKO)
    rs.add_edge("maladie_virale",        "maladie_infectieuse",   SemanticNetwork.LINK_AKO)
    rs.add_edge("maladie_bacterienne",   "maladie_infectieuse",   SemanticNetwork.LINK_AKO)
    rs.add_edge("maladie_parasitaire",   "maladie_infectieuse",   SemanticNetwork.LINK_AKO)
    rs.add_edge("maladie_fongique",      "maladie_infectieuse",   SemanticNetwork.LINK_AKO)
    rs.add_edge("maladie_chronique",     "maladie",               SemanticNetwork.LINK_AKO)
    rs.add_edge("maladie_aigue",         "maladie",               SemanticNetwork.LINK_AKO)
    rs.add_edge("maladie_respiratoire",  "maladie_infectieuse",   SemanticNetwork.LINK_AKO)
    rs.add_edge("maladie_vectorielle",   "maladie_infectieuse",   SemanticNetwork.LINK_AKO)
    rs.add_edge("maladie_enterique",     "maladie_infectieuse",   SemanticNetwork.LINK_AKO)
    rs.add_edge("maladie_sexuellement_transmissible", "maladie_infectieuse", SemanticNetwork.LINK_AKO)
    rs.add_edge("maladie_neurologique_infectieuse",   "maladie_infectieuse", SemanticNetwork.LINK_AKO)

    # Agents pathogènes → hiérarchie
    rs.add_edge("virus",      "agent_pathogene",  SemanticNetwork.LINK_AKO)
    rs.add_edge("bacterie",   "agent_pathogene",  SemanticNetwork.LINK_AKO)
    rs.add_edge("parasite",   "agent_pathogene",  SemanticNetwork.LINK_AKO)
    rs.add_edge("champignon", "agent_pathogene",  SemanticNetwork.LINK_AKO)

    # Agents pathogènes → maladies
    rs.add_edge("virus",      "maladie_virale",      SemanticNetwork.LINK_CAUSES)
    rs.add_edge("bacterie",   "maladie_bacterienne", SemanticNetwork.LINK_CAUSES)
    rs.add_edge("parasite",   "maladie_parasitaire", SemanticNetwork.LINK_CAUSES)
    rs.add_edge("champignon", "maladie_fongique",    SemanticNetwork.LINK_CAUSES)
    rs.add_edge("agent_pathogene", "maladie_infectieuse", SemanticNetwork.LINK_CAUSES)

    # Traitements
    rs.add_edge("antibiotique",    "maladie_bacterienne", SemanticNetwork.LINK_TREATS)
    rs.add_edge("antiviral",       "maladie_virale",      SemanticNetwork.LINK_TREATS)
    rs.add_edge("antiparasitaire", "maladie_parasitaire", SemanticNetwork.LINK_TREATS)
    rs.add_edge("antifongique",    "maladie_fongique",    SemanticNetwork.LINK_TREATS)
    rs.add_edge("vaccin",          "maladie_virale",      SemanticNetwork.LINK_TREATS,
                is_default=True)
    rs.add_edge("vaccin",          "maladie_bacterienne", SemanticNetwork.LINK_TREATS,
                is_default=True)

    # ════════════════════════════════════════════════════════════════════
    #  INSTANCES CONCRÈTES
    # ════════════════════════════════════════════════════════════════════

    # COVID-19 : maladie virale ET respiratoire
    rs.add_edge("COVID-19",  "maladie_virale",       SemanticNetwork.LINK_ISA)
    rs.add_edge("COVID-19",  "maladie_respiratoire", SemanticNetwork.LINK_ISA)

    # Tuberculose : maladie bactérienne ET respiratoire (ET chronique)
    rs.add_edge("tuberculose", "maladie_bacterienne", SemanticNetwork.LINK_ISA)
    rs.add_edge("tuberculose", "maladie_respiratoire",SemanticNetwork.LINK_ISA)
    rs.add_edge("tuberculose", "maladie_chronique",   SemanticNetwork.LINK_ISA)

    # Paludisme : parasitaire vectorielle
    rs.add_edge("paludisme", "maladie_parasitaire",  SemanticNetwork.LINK_ISA)
    rs.add_edge("paludisme", "maladie_vectorielle",  SemanticNetwork.LINK_ISA)

    # Méningite bactérienne : bactérienne + neurologique
    rs.add_edge("meningite_bacterienne", "maladie_bacterienne",             SemanticNetwork.LINK_ISA)
    rs.add_edge("meningite_bacterienne", "maladie_neurologique_infectieuse",SemanticNetwork.LINK_ISA)

    # Grippe : virale respiratoire
    rs.add_edge("grippe",     "maladie_virale",       SemanticNetwork.LINK_ISA)
    rs.add_edge("grippe",     "maladie_respiratoire", SemanticNetwork.LINK_ISA)

    # Choléra : bactérienne entérique
    rs.add_edge("cholera",    "maladie_bacterienne",  SemanticNetwork.LINK_ISA)
    rs.add_edge("cholera",    "maladie_enterique",    SemanticNetwork.LINK_ISA)

    # Candidose : fongique
    rs.add_edge("candidose",  "maladie_fongique",     SemanticNetwork.LINK_ISA)

    # VIH : virale sexuellement transmissible + chronique
    rs.add_edge("VIH",        "maladie_virale",                        SemanticNetwork.LINK_ISA)
    rs.add_edge("VIH",        "maladie_sexuellement_transmissible",    SemanticNetwork.LINK_ISA)
    rs.add_edge("VIH",        "maladie_chronique",                     SemanticNetwork.LINK_ISA)

    # Bactérie BMR
    rs.add_edge("bacterie_BMR", "bacterie",  SemanticNetwork.LINK_ISA)

    # Botulisme
    rs.add_edge("botulisme",    "maladie_bacterienne", SemanticNetwork.LINK_ISA)

    # ════════════════════════════════════════════════════════════════════
    #  LIENS D'EXCEPTION (Partie 3)
    # ════════════════════════════════════════════════════════════════════

    # K31 : BMR résistante aux antibiotiques
    # → Exception : "antibiotique" ne traite PAS bacterie_BMR
    rs.add_edge("antibiotique", "bacterie_BMR",
                SemanticNetwork.LINK_TREATS,
                is_exception=True)
    # On marque sur le nœud lui-même
    rs.nodes["bacterie_BMR"].add_exception(SemanticNetwork.LINK_TREATS)

    # K32/K33 : botulisme ne provoque PAS de fièvre (exception au défaut bactérien)
    rs.nodes["botulisme"].add_property("provoque", "paralysie_flasque")
    rs.nodes["botulisme"].add_exception("provoque_fièvre")
    # On surcharge explicitement la propriété héritée
    rs.nodes["botulisme"].properties["provoque"] = "paralysie_flasque"

    # ════════════════════════════════════════════════════════════════════
    #  LIENS MODAUX
    # ════════════════════════════════════════════════════════════════════

    rs.add_edge("OMS",                   "COVID-19",      SemanticNetwork.LINK_KNOWS)
    rs.add_edge("chercheurs_en_virologie","antiviral",    SemanticNetwork.LINK_BELIEVES)
    rs.add_edge("gouvernements",         "vaccin",        SemanticNetwork.LINK_WANTS)

    return rs


# ═══════════════════════════════════════════════════════════════════════════
#  SECTION 3 – REQUÊTES DE DÉMONSTRATION
# ═══════════════════════════════════════════════════════════════════════════

def run_demo(rs: SemanticNetwork):
    """
    Exécute une série de requêtes illustrant les trois parties du TP.
    """

    separator = "\n" + "═" * 65

    # ──────────────────────────────────────────────────────────────────
    print(separator)
    print("  PARTIE 1 – PROPAGATION DE MARQUEURS")
    print(separator)

    # Q1 : Quelles maladies se transmettent par voie aérienne ?
    #      → chercher tous les nœuds qui ont le lien is-a / a-kind-of
    #        vers maladie_respiratoire (direction inverse)
    print("\n  ❓ Q1 : Quelles sont les maladies transmises par voie aérienne ?")
    print("      (= instances et sous-classes de maladie_respiratoire)")
    result1 = rs.marker_propagation(
        start_nodes=["maladie_respiratoire"],
        target_relation=SemanticNetwork.LINK_ISA,
        direction="backward",
        verbose=True
    )
    print(f"  → Réponse Q1 : {result1}\n")

    # Q2 : Quels traitements existent pour les maladies virales ?
    print("  ❓ Q2 : Quels traitements traitent les maladies virales "
          "(directement ou via héritage) ?")
    result2 = rs.marker_propagation(
        start_nodes=["maladie_virale", "maladie_infectieuse"],
        target_relation=SemanticNetwork.LINK_TREATS,
        direction="backward",
        verbose=True
    )
    print(f"  → Réponse Q2 : {result2}\n")

    # Q3 : Quels agents causent des maladies respiratoires ?
    print("  ❓ Q3 : Quels agents pathogènes provoquent des maladies respiratoires ?")
    # D'abord trouver les sous-classes de maladie_respiratoire,
    # puis voir quels agents les causent
    resp_diseases = rs.marker_propagation(
        start_nodes=["maladie_respiratoire"],
        target_relation=SemanticNetwork.LINK_ISA,
        direction="backward",
        verbose=False
    ) + ["maladie_respiratoire"]

    result3 = rs.marker_propagation(
        start_nodes=resp_diseases,
        target_relation=SemanticNetwork.LINK_CAUSES,
        direction="backward",
        verbose=True
    )
    print(f"  → Réponse Q3 : {result3}\n")

    # ──────────────────────────────────────────────────────────────────
    print(separator)
    print("  PARTIE 2 – HÉRITAGE ET SATURATION")
    print(separator)

    # H1 : Toutes les propriétés de la COVID-19
    print("\n  ❓ H1 : Quelles sont TOUTES les propriétés héritées par la COVID-19 ?")
    covid_props = rs.inherit_properties("COVID-19", verbose=True)

    # H2 : Toutes les propriétés du paludisme
    print("\n  ❓ H2 : Quelles sont TOUTES les propriétés héritées par le paludisme ?")
    palu_props = rs.inherit_properties("paludisme", verbose=True)

    # H3 : Saturation du réseau entier
    print("\n  ❓ H3 : Saturation totale du réseau (clôture de l'héritage)")
    nb = rs.saturate(verbose=True)

    # ──────────────────────────────────────────────────────────────────
    print(separator)
    print("  PARTIE 3 – PROPAGATION AVEC INHIBITION DES EXCEPTIONS")
    print(separator)

    # E1 : L'antibiotique traite-t-il la bactérie BMR ?
    print("\n  ❓ E1 : Quelles bactéries sont traitées par les antibiotiques ?")
    print("      (en tenant compte de la résistance de BMR)\n")
    result_e1 = rs.propagate_with_exception_inhibition(
        start_node="antibiotique",
        relation=SemanticNetwork.LINK_TREATS,
        verbose=True
    )
    print(f"  → Réponse E1 : {result_e1}")

    # E2 : Héritage du botulisme avec exception sur "provoque"
    print("\n  ❓ E2 : Propriétés héritées par le botulisme "
          "(exception : ne provoque PAS de fièvre)\n")
    botul_props = rs.inherit_properties("botulisme",
                                        respect_exceptions=True,
                                        verbose=True)
    print(f"  → Résultat E2 : {botul_props}")

    # Comparaison avec/sans exception
    print("\n  ❓ E3 : Même chose SANS respecter les exceptions (héritage naïf)\n")
    botul_naive = rs.inherit_properties("botulisme",
                                        respect_exceptions=False,
                                        verbose=True)
    print(f"  → Résultat E3 (naïf) : {botul_naive}")

    print("\n  💡 Conclusion : Le respect des exceptions empêche l'héritage")
    print("     incorrect de 'provoque=fièvre' pour le botulisme.")


# ═══════════════════════════════════════════════════════════════════════════
#  SECTION 4 – CLASSE UTILITAIRE : REQUÊTES EN LANGAGE NATUREL
# ═══════════════════════════════════════════════════════════════════════════

class MedicalQA:
    """
    Interface de requêtes en langage naturel sur le réseau médical.
    Permet de poser des questions sous forme de méthodes nommées.
    """

    def __init__(self, network: SemanticNetwork):
        self.rs = network

    def _subclasses_and_instances(self, concept: str) -> list[str]:
        """Retourne toutes les sous-classes et instances d'un concept."""
        return self.rs.marker_propagation(
            start_nodes=[concept],
            target_relation=SemanticNetwork.LINK_ISA,
            direction="backward",
            verbose=False
        ) + self.rs.marker_propagation(
            start_nodes=[concept],
            target_relation=SemanticNetwork.LINK_AKO,
            direction="backward",
            verbose=False
        )

    def maladies_traitees_par(self, traitement: str) -> list[str]:
        """Quelles maladies sont traitées par un traitement donné ?"""
        return self.rs.marker_propagation(
            start_nodes=[traitement],
            target_relation=SemanticNetwork.LINK_TREATS,
            direction="forward",
            verbose=False
        )

    def traitements_pour(self, maladie: str) -> list[str]:
        """Quels traitements existe-t-il pour une maladie donnée ?"""
        # Remonter les types de la maladie
        ancestors = [maladie] + self._subclasses_and_instances(maladie)
        return self.rs.marker_propagation(
            start_nodes=ancestors,
            target_relation=SemanticNetwork.LINK_TREATS,
            direction="backward",
            verbose=False
        )

    def transmission_de(self, maladie: str) -> Optional[str]:
        """Quel est le mode de transmission d'une maladie ?"""
        props = self.rs.inherit_properties(maladie, verbose=False)
        return props.get("transmission", (None,))[0] if "transmission" in props else None

    def symptomes_de(self, maladie: str) -> list[str]:
        """Quels symptômes / effets provoque une maladie ?"""
        props = self.rs.inherit_properties(maladie, verbose=False)
        symptoms = []
        for key, (val, src, _) in props.items():
            if "provoque" in key:
                symptoms.append(val)
        return symptoms

    def rapport_complet(self, entite: str):
        """Génère un rapport complet sur une entité du réseau."""
        print(f"\n{'═'*65}")
        print(f"  RAPPORT COMPLET : {entite.upper()}")
        print(f"{'═'*65}")

        if entite not in self.rs.nodes:
            print(f"  ⚠ Entité '{entite}' introuvable dans le réseau.")
            return

        node = self.rs.nodes[entite]
        print(f"  Type de nœud    : {node.node_type}")
        print(f"  Propriétés directes : {node.properties}")
        print(f"  Exceptions déclarées : {node.exceptions or 'aucune'}")

        ancestors = self.rs._get_ancestors(entite)
        print(f"\n  Ancêtres (hiérarchie) :")
        for anc in ancestors:
            print(f"     ↑ {anc}")

        all_props = self.rs.inherit_properties(entite, verbose=False)
        print(f"\n  Toutes les propriétés héritées :")
        for prop, (val, source, is_def) in sorted(all_props.items()):
            tag = " (défaut)" if is_def else ""
            print(f"     • {prop:35s} = {val!s:20s}  ← {source}{tag}")

        traitements = self.traitements_pour(entite)
        print(f"\n  Traitements applicables :")
        if traitements:
            for t in traitements:
                print(f"     💊 {t}")
        else:
            print("     (aucun traitement identifié)")

        transmission = self.transmission_de(entite)
        print(f"\n  Mode de transmission : {transmission or 'non spécifié'}")

        print(f"{'═'*65}\n")


# ═══════════════════════════════════════════════════════════════════════════
#  SECTION 5 – POINT D'ENTRÉE PRINCIPAL
# ═══════════════════════════════════════════════════════════════════════════

def main():
    print("""
╔═══════════════════════════════════════════════════════════════╗
║  TP 5 – Réseaux Sémantiques                                   ║
║  Propagation de marqueurs · Héritage · Inhibition exceptions  ║
║  Exemple : Domaine Médical – Maladies Infectieuses            ║
║  Master 1 SII – USTHB 2025-2026                               ║
╚═══════════════════════════════════════════════════════════════╝
    """)

    # ── Étape 1 : Construction du réseau ────────────────────────────────
    print("  [1/4] Construction du réseau sémantique médical...")
    rs = build_medical_network()
    rs.display()

    # ── Étape 2 : Démonstration des trois parties ────────────────────────
    print("  [2/4] Exécution des démonstrations (Parties 1, 2, 3)...")
    run_demo(rs)

    # ── Étape 3 : Interface QA ───────────────────────────────────────────
    print("\n" + "═" * 65)
    print("  [3/4] INTERFACE QA – RAPPORTS COMPLETS")
    print("═" * 65)

    qa = MedicalQA(rs)

    # Rapports sur plusieurs maladies
    for entite in ["COVID-19", "tuberculose", "paludisme",
                   "botulisme", "bacterie_BMR", "meningite_bacterienne"]:
        qa.rapport_complet(entite)

    # ── Étape 4 : Requêtes ciblées ───────────────────────────────────────
    print("\n" + "═" * 65)
    print("  [4/4] REQUÊTES CIBLÉES EN LANGAGE NATUREL")
    print("═" * 65)

    questions = [
        ("Quelles maladies sont traitées par les antiviraux ?",
         lambda: qa.maladies_traitees_par("antiviral")),

        ("Quels traitements pour la méningite bactérienne ?",
         lambda: qa.traitements_pour("meningite_bacterienne")),

        ("Quels symptômes provoque la grippe ?",
         lambda: qa.symptomes_de("grippe")),

        ("Comment se transmet le choléra ?",
         lambda: qa.transmission_de("cholera")),

        ("Quelles maladies se transmettent par vecteur ?",
         lambda: rs.marker_propagation(
             ["maladie_vectorielle"],
             SemanticNetwork.LINK_ISA,
             "backward",
             verbose=False
         )),

        ("Quelles maladies provoquent une détresse respiratoire ?",
         lambda: rs.marker_propagation(
             ["maladie_respiratoire"],
             SemanticNetwork.LINK_ISA,
             "backward",
             verbose=False
         )),
    ]

    for question, fn in questions:
        print(f"\n  ❓ {question}")
        answer = fn()
        if isinstance(answer, list):
            if answer:
                for a in answer:
                    print(f"     → {a}")
            else:
                print("     → (aucun résultat)")
        else:
            print(f"     → {answer}")

    print("\n" + "═" * 65)
    print("  ✅ Fin de l'exécution du TP5")
    print("═" * 65)


# ── Lancement ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    main()