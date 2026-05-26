"""
=============================================================================
TP 5 — Logiques de Description
Domaine : La Restauration & la Cuisine Mondiale
USTHB — Master 1 SII — Représentation et Raisonnement 1 — 2025/2026
=============================================================================

CONCEPTS ATOMIQUES :
  RESTAURANT, CUISINE, CHEF, PLAT, INGREDIENT, CERTIFICATION, BOISSON

RÔLES ATOMIQUES :
  propose, emploie, prepare, contient, possede, accompagne

=============================================================================
SECTION 1 — SYNTAXE RACER (commentaires)
=============================================================================

(in-knowledge-base restauration kb-restauration)

(signature
  :atomic-concepts (
    RESTAURANT CUISINE CHEF PLAT INGREDIENT CERTIFICATION BOISSON
    PRODUIT-LOCAL VIANDE ALLERGEN CHEF-CERTIFIE)
  :roles (
    (propose    :comment "un restaurant propose des plats")
    (emploie    :comment "un restaurant emploie des chefs")
    (prepare    :comment "un chef prepare des plats")
    (contient   :comment "un plat contient des ingredients")
    (possede    :comment "un restaurant possede une certification")
    (accompagne :comment "un plat accompagne une boisson"))
  :individuals (
    le-jules-verne la-tour-argent chez-omar mcdonalds le-jardin-vert
    chef-ducasse chef-robuchon chef-sara
    boeuf-bourguignon couscous-royal burger-vegan
    soupe-tomate tarte-tatin salade-nicoise
    etoile-michelin label-bio
    truffe agneau pois-chiche lactose
    vin-bordeaux eau-minerale))

; ===== TBox =====

; (a) Restaurant Gastronomique :
;     RESTAURANT ⊓ ≥1 emploie.CHEF ⊓ ≥5 propose.PLAT ⊓ ≥1 possede.CERTIFICATION
(equivalent RESTAURANT-GASTRONOMIQUE
  (and RESTAURANT
       (at-least 1 emploie CHEF)
       (at-least 5 propose PLAT)
       (at-least 1 possede CERTIFICATION)))

; (b) Restaurant Etoile :
;     RESTAURANT-GASTRONOMIQUE ⊓ ∃possede.ETOILE-MICHELIN
(equivalent RESTAURANT-ETOILE
  (and RESTAURANT-GASTRONOMIQUE
       (some possede ETOILE-MICHELIN)))

; (c) Restaurant Bistronomique :
;     RESTAURANT ⊓ ¬(∃possede.CERTIFICATION)
(equivalent RESTAURANT-BISTRONOMIQUE
  (and RESTAURANT
       (not (some possede CERTIFICATION))))

; (d) Restaurant Vegetarien :
;     RESTAURANT ⊓ ∀propose.(PLAT ⊓ ¬∃contient.VIANDE)
(equivalent RESTAURANT-VEGETARIEN
  (and RESTAURANT
       (all propose (and PLAT (not (some contient VIANDE))))))

; (e) Restaurant Rapide :
;     RESTAURANT ⊓ ≤3 propose.PLAT
(equivalent RESTAURANT-RAPIDE
  (and RESTAURANT
       (at-most 3 propose PLAT)))

; (f) Chef Etoile :
;     CHEF ⊓ ∃prepare.PLAT ⊓ ∃possede.CHEF-CERTIFIE
(equivalent CHEF-ETOILE
  (and CHEF
       (some prepare PLAT)
       (some possede CHEF-CERTIFIE)))

; (g) Plat Signature :
;     PLAT ⊓ ∃contient.PRODUIT-LOCAL ⊓ ≥1 accompagne.BOISSON
(equivalent PLAT-SIGNATURE
  (and PLAT
       (some contient PRODUIT-LOCAL)
       (at-least 1 accompagne BOISSON)))

; (h) Disjonction
(disjoint RESTAURANT-GASTRONOMIQUE RESTAURANT-RAPIDE)

; (i) Tout restaurant propose au moins un plat
(implies RESTAURANT (at-least 1 propose PLAT))

; (j) Tout plat signature accompagne au moins une boisson
(implies PLAT-SIGNATURE (at-least 1 accompagne BOISSON))

; ===== ABox =====

(instance le-jules-verne   RESTAURANT-ETOILE)
(instance la-tour-argent   RESTAURANT-GASTRONOMIQUE)
(instance chez-omar        RESTAURANT-BISTRONOMIQUE)
(instance mcdonalds        RESTAURANT-RAPIDE)
(instance le-jardin-vert   RESTAURANT-VEGETARIEN)

(instance chef-ducasse     CHEF-ETOILE)
(instance chef-robuchon    CHEF-ETOILE)
(instance chef-sara        CHEF)

(instance boeuf-bourguignon PLAT-SIGNATURE)
(instance couscous-royal    PLAT)
(instance burger-vegan      PLAT)

(related le-jules-verne  chef-ducasse       emploie)
(related le-jules-verne  boeuf-bourguignon  propose)
(related le-jules-verne  etoile-michelin    possede)
(related la-tour-argent  chef-robuchon      emploie)
(related la-tour-argent  label-bio          possede)
(related chez-omar       chef-sara          emploie)
(related chez-omar       couscous-royal     propose)
(related mcdonalds       burger-vegan       propose)
(related chef-ducasse    boeuf-bourguignon  prepare)
(related boeuf-bourguignon truffe           contient)
(related boeuf-bourguignon vin-bordeaux     accompagne)

; ===== Requetes =====
#|
(concept-subsumes? RESTAURANT-GASTRONOMIQUE RESTAURANT-ETOILE)
(concept-ancestors RESTAURANT-ETOILE)
(concept-descendants RESTAURANT)
(individual-instance? le-jules-verne RESTAURANT-GASTRONOMIQUE)
(individual-types chef-ducasse)
(concept-instances RESTAURANT-ETOILE)
(concept-instances CHEF-ETOILE)
(individual-fillers le-jules-verne propose)
|#

=============================================================================
"""

# =============================================================================
# SECTION 2 — IMPLEMENTATION PYTHON avec owlready2
# =============================================================================

from owlready2 import *

print("=" * 70)
print("  TP 5 — Logiques de Description : Domaine Restauration & Cuisine")
print("  USTHB — Master 1 SII — 2025/2026")
print("=" * 70)

# -----------------------------------------------------------------------------
# Creation de l'ontologie
# -----------------------------------------------------------------------------
onto = get_ontology("http://usthb.dz/restauration.owl")

with onto:

    # =========================================================================
    # CONCEPTS ATOMIQUES
    # =========================================================================
    class RESTAURANT(Thing):   pass
    class CUISINE(Thing):      pass
    class CHEF(Thing):         pass
    class PLAT(Thing):         pass
    class INGREDIENT(Thing):   pass
    class CERTIFICATION(Thing):pass
    class BOISSON(Thing):      pass

    # Sous-concepts atomiques d'INGREDIENT
    class PRODUIT_LOCAL(INGREDIENT): pass
    class VIANDE(INGREDIENT):        pass
    class ALLERGEN(INGREDIENT):      pass

    # Sous-concept de CERTIFICATION pour les chefs
    class CHEF_CERTIFIE(CERTIFICATION): pass

    # Sous-concept de CERTIFICATION pour les etoiles
    class ETOILE_MICHELIN(CERTIFICATION): pass

    # =========================================================================
    # ROLES ATOMIQUES
    # =========================================================================
    class propose(ObjectProperty):
        domain = [RESTAURANT]
        range  = [PLAT]

    class emploie(ObjectProperty):
        domain = [RESTAURANT]
        range  = [CHEF]

    class prepare(ObjectProperty):
        domain = [CHEF]
        range  = [PLAT]

    class contient(ObjectProperty):
        domain = [PLAT]
        range  = [INGREDIENT]

    class possede(ObjectProperty):
        # domaine mixte : RESTAURANT ou CHEF
        range  = [CERTIFICATION]

    class accompagne(ObjectProperty):
        domain = [PLAT]
        range  = [BOISSON]

    # =========================================================================
    # TBox — Definitions de concepts complexes
    # =========================================================================

    # (a) RESTAURANT_GASTRONOMIQUE
    #     RESTAURANT ⊓ ≥1 emploie.CHEF ⊓ ≥5 propose.PLAT ⊓ ≥1 possede.CERTIFICATION
    class RESTAURANT_GASTRONOMIQUE(RESTAURANT):
        equivalent_to = [
            RESTAURANT
            & emploie.min(1, CHEF)
            & propose.min(5, PLAT)
            & possede.min(1, CERTIFICATION)
        ]

    # (b) RESTAURANT_ETOILE
    #     RESTAURANT_GASTRONOMIQUE ⊓ ∃possede.ETOILE_MICHELIN
    class RESTAURANT_ETOILE(RESTAURANT_GASTRONOMIQUE):
        equivalent_to = [
            RESTAURANT_GASTRONOMIQUE
            & possede.some(ETOILE_MICHELIN)
        ]

    # (c) RESTAURANT_BISTRONOMIQUE
    #     RESTAURANT ⊓ ¬(∃possede.CERTIFICATION)
    class RESTAURANT_BISTRONOMIQUE(RESTAURANT):
        equivalent_to = [
            RESTAURANT
            & Not(possede.some(CERTIFICATION))
        ]

    # (d) RESTAURANT_VEGETARIEN
    #     RESTAURANT ⊓ ∀propose.(PLAT ⊓ ¬∃contient.VIANDE)
    class RESTAURANT_VEGETARIEN(RESTAURANT):
        equivalent_to = [
            RESTAURANT
            & propose.only(PLAT & Not(contient.some(VIANDE)))
        ]

    # (e) RESTAURANT_RAPIDE
    #     RESTAURANT ⊓ ≤3 propose.PLAT
    class RESTAURANT_RAPIDE(RESTAURANT):
        equivalent_to = [
            RESTAURANT
            & propose.max(3, PLAT)
        ]

    # (f) CHEF_ETOILE  — corrige : CHEF ⊓ ∃prepare.PLAT ⊓ ∃possede.CHEF_CERTIFIE
    #     Le critere possede.CHEF_CERTIFIE distingue chef_sara des chefs etoiles
    class CHEF_ETOILE(CHEF):
        equivalent_to = [
            CHEF
            & prepare.some(PLAT)
            & possede.some(CHEF_CERTIFIE)
        ]

    # (g) PLAT_SIGNATURE
    #     PLAT ⊓ ∃contient.PRODUIT_LOCAL ⊓ ≥1 accompagne.BOISSON
    class PLAT_SIGNATURE(PLAT):
        equivalent_to = [
            PLAT
            & contient.some(PRODUIT_LOCAL)
            & accompagne.min(1, BOISSON)
        ]

    # (h) Disjonction : RESTAURANT_GASTRONOMIQUE ⊓ RESTAURANT_RAPIDE = ⊥
    AllDisjoint([RESTAURANT_GASTRONOMIQUE, RESTAURANT_RAPIDE])

    # (i) Tout restaurant propose au moins un plat
    RESTAURANT.is_a.append(propose.min(1, PLAT))

    # (j) Tout plat signature accompagne au moins une boisson
    PLAT_SIGNATURE.is_a.append(accompagne.min(1, BOISSON))

    # =========================================================================
    # ABox — Assertions sur les individus
    # =========================================================================

    # --- Certifications ---
    etoile_michelin  = ETOILE_MICHELIN("etoile_michelin")
    label_bio        = CERTIFICATION("label_bio")
    cert_ducasse     = CHEF_CERTIFIE("cert_ducasse")
    cert_robuchon    = CHEF_CERTIFIE("cert_robuchon")

    # --- Boissons ---
    vin_bordeaux     = BOISSON("vin_bordeaux")
    eau_minerale     = BOISSON("eau_minerale")

    # --- Ingredients ---
    truffe           = PRODUIT_LOCAL("truffe")
    agneau           = VIANDE("agneau")
    pois_chiche      = INGREDIENT("pois_chiche")
    lactose          = ALLERGEN("lactose")

    # --- Plats ---
    # boeuf_bourguignon = PLAT_SIGNATURE car contient truffe (PRODUIT_LOCAL)
    #                     et accompagne vin_bordeaux (BOISSON)
    boeuf_bourguignon = PLAT_SIGNATURE("boeuf_bourguignon")
    boeuf_bourguignon.contient   = [truffe]
    boeuf_bourguignon.accompagne = [vin_bordeaux]

    couscous_royal    = PLAT("couscous_royal")
    couscous_royal.contient = [agneau, pois_chiche]

    burger_vegan      = PLAT("burger_vegan")
    soupe_tomate      = PLAT("soupe_tomate")
    tarte_tatin       = PLAT("tarte_tatin")
    salade_nicoise    = PLAT("salade_nicoise")

    # --- Chefs ---
    # chef_ducasse et chef_robuchon sont CHEF_ETOILE
    # car ils preparent des plats ET possedent une certification
    chef_ducasse = CHEF_ETOILE("chef_ducasse")
    chef_ducasse.prepare = [boeuf_bourguignon, tarte_tatin]
    chef_ducasse.possede = [cert_ducasse]

    chef_robuchon = CHEF_ETOILE("chef_robuchon")
    chef_robuchon.prepare = [soupe_tomate, salade_nicoise]
    chef_robuchon.possede = [cert_robuchon]

    # chef_sara = CHEF simple (pas de certification)
    chef_sara = CHEF("chef_sara")
    chef_sara.prepare = [couscous_royal]
    # chef_sara ne possede aucune CHEF_CERTIFIE => ne sera PAS CHEF_ETOILE

    # --- Restaurants ---

    # Le Jules Verne : RESTAURANT_ETOILE
    le_jules_verne = RESTAURANT_ETOILE("le_jules_verne")
    le_jules_verne.emploie = [chef_ducasse]
    le_jules_verne.propose = [boeuf_bourguignon, tarte_tatin,
                               soupe_tomate, salade_nicoise, salade_nicoise]
    le_jules_verne.possede = [etoile_michelin]

    # Correction : 5 plats distincts pour satisfaire ≥5 propose.PLAT
    le_jules_verne.propose = [boeuf_bourguignon, tarte_tatin,
                               soupe_tomate, salade_nicoise, couscous_royal]

    # La Tour d'Argent : RESTAURANT_GASTRONOMIQUE (sans etoile Michelin)
    la_tour_argent = RESTAURANT_GASTRONOMIQUE("la_tour_argent")
    la_tour_argent.emploie = [chef_robuchon]
    la_tour_argent.propose = [couscous_royal, soupe_tomate,
                               boeuf_bourguignon, tarte_tatin, salade_nicoise]
    la_tour_argent.possede = [label_bio]

    # Chez Omar : RESTAURANT_BISTRONOMIQUE (sans certification)
    chez_omar = RESTAURANT_BISTRONOMIQUE("chez_omar")
    chez_omar.emploie = [chef_sara]
    chez_omar.propose = [couscous_royal]

    # McDonald's : RESTAURANT_RAPIDE (au plus 3 plats)
    mcdonalds = RESTAURANT_RAPIDE("mcdonalds")
    mcdonalds.propose = [burger_vegan]

    # Le Jardin Vert : RESTAURANT_VEGETARIEN
    # Tous ses plats ne contiennent pas de viande
    le_jardin_vert = RESTAURANT_VEGETARIEN("le_jardin_vert")
    le_jardin_vert.propose = [burger_vegan, soupe_tomate]

    # Unicite des individus
    AllDifferent([le_jules_verne, la_tour_argent, chez_omar,
                  mcdonalds, le_jardin_vert])
    AllDifferent([chef_ducasse, chef_robuchon, chef_sara])
    AllDifferent([boeuf_bourguignon, couscous_royal, burger_vegan,
                  soupe_tomate, tarte_tatin, salade_nicoise])


# =============================================================================
# SECTION 3 — AFFICHAGE AVANT RAISONNEMENT
# =============================================================================

print("\n" + "─" * 70)
print("  SECTION 1 — INSPECTION DE LA TBox")
print("─" * 70)

print("\n[Hierarchie des concepts]")
for concept_name, concept_cls in [
    ("RESTAURANT", RESTAURANT),
    ("CHEF",       CHEF),
    ("PLAT",       PLAT),
    ("INGREDIENT", INGREDIENT),
    ("CERTIFICATION", CERTIFICATION),
]:
    subs = list(concept_cls.subclasses())
    if subs:
        print(f"  Sous-concepts de {concept_name} :")
        for s in subs:
            print(f"    ▸ {s.name}")

print("\n" + "─" * 70)
print("  SECTION 2 — INSPECTION DE LA ABox (avant raisonnement)")
print("─" * 70)

print("\n[Individus declares par concept]")
concepts_to_check = [
    ("RESTAURANT",               RESTAURANT),
    ("RESTAURANT_GASTRONOMIQUE", RESTAURANT_GASTRONOMIQUE),
    ("RESTAURANT_ETOILE",        RESTAURANT_ETOILE),
    ("RESTAURANT_BISTRONOMIQUE", RESTAURANT_BISTRONOMIQUE),
    ("RESTAURANT_RAPIDE",        RESTAURANT_RAPIDE),
    ("RESTAURANT_VEGETARIEN",    RESTAURANT_VEGETARIEN),
    ("CHEF",                     CHEF),
    ("CHEF_ETOILE",              CHEF_ETOILE),
    ("PLAT",                     PLAT),
    ("PLAT_SIGNATURE",           PLAT_SIGNATURE),
    ("INGREDIENT",               INGREDIENT),
    ("ALLERGEN",                 ALLERGEN),
    ("CERTIFICATION",            CERTIFICATION),
    ("ETOILE_MICHELIN",          ETOILE_MICHELIN),
    ("CHEF_CERTIFIE",            CHEF_CERTIFIE),
]
for name, cls in concepts_to_check:
    instances = list(cls.instances())
    if instances:
        noms = ", ".join(i.name for i in instances)
        print(f"  {name:30s} → {noms}")

print("\n[Relations (roles) des individus]")
individus_affichage = [
    le_jules_verne, la_tour_argent, chez_omar, mcdonalds, le_jardin_vert,
    chef_ducasse, chef_robuchon, chef_sara,
    boeuf_bourguignon, couscous_royal
]
for ind in individus_affichage:
    infos = []
    if hasattr(ind, 'emploie')    and ind.emploie:
        infos.append("emploie="    + str([c.name for c in ind.emploie]))
    if hasattr(ind, 'propose')    and ind.propose:
        infos.append("propose="    + str([p.name for p in ind.propose
                                          if hasattr(p, 'name')]))
    if hasattr(ind, 'possede')    and ind.possede:
        infos.append("possede="    + str([c.name for c in ind.possede]))
    if hasattr(ind, 'prepare')    and ind.prepare:
        infos.append("prepare="    + str([p.name for p in ind.prepare]))
    if hasattr(ind, 'contient')   and ind.contient:
        infos.append("contient="   + str([i.name for i in ind.contient]))
    if hasattr(ind, 'accompagne') and ind.accompagne:
        infos.append("accompagne=" + str([b.name for b in ind.accompagne]))
    if infos:
        print(f"  {ind.name:25s} : {', '.join(infos)}")


# =============================================================================
# SECTION 4 — RAISONNEMENT HermiT
# =============================================================================

print("\n" + "─" * 70)
print("  SECTION 3 — RAISONNEMENT (HermiT Reasoner)")
print("─" * 70)

try:
    sync_reasoner_hermit(infer_property_values=True, debug=0)
    print("\n  ✓ Raisonnement HermiT termine avec succes.")
except Exception as e:
    print(f"\n  ⚠ HermiT non disponible : {e}")


# =============================================================================
# SECTION 5 — REQUETES DE RAISONNEMENT
# =============================================================================

print("\n" + "─" * 70)
print("  SECTION 4 — REQUETES DE RAISONNEMENT")
print("─" * 70)

# Q1 — Subsomption
print("\n[Q1] Subsomption : RESTAURANT_ETOILE ⊑ RESTAURANT_GASTRONOMIQUE ?")
print(f"  → {issubclass(RESTAURANT_ETOILE, RESTAURANT_GASTRONOMIQUE)}"
      "  (tout restaurant etoile est gastronomique)")

print("\n[Q2] Subsomption : RESTAURANT_RAPIDE ⊑ RESTAURANT_GASTRONOMIQUE ?")
print(f"  → {issubclass(RESTAURANT_RAPIDE, RESTAURANT_GASTRONOMIQUE)}"
      "  (disjoints — impossible)")

print("\n[Q3] Subsomption : CHEF_ETOILE ⊑ CHEF ?")
print(f"  → {issubclass(CHEF_ETOILE, CHEF)}")

# Q2 — Appartenance individu / concept
print("\n[Q4] Le Jules Verne est-il un RESTAURANT_ETOILE ?")
print(f"  → {isinstance(le_jules_verne, RESTAURANT_ETOILE)}")

print("\n[Q5] Le Jules Verne est-il un RESTAURANT_GASTRONOMIQUE ?")
print(f"  → {isinstance(le_jules_verne, RESTAURANT_GASTRONOMIQUE)}"
      "  (infere : tout etoile est gastronomique)")

print("\n[Q6] Chez Omar est-il un RESTAURANT_GASTRONOMIQUE ?")
print(f"  → {isinstance(chez_omar, RESTAURANT_GASTRONOMIQUE)}")

print("\n[Q7] McDonald's est-il un RESTAURANT_RAPIDE ?")
print(f"  → {isinstance(mcdonalds, RESTAURANT_RAPIDE)}")

print("\n[Q8] McDonald's est-il un RESTAURANT_GASTRONOMIQUE ?")
print(f"  → {isinstance(mcdonalds, RESTAURANT_GASTRONOMIQUE)}"
      "  (disjonction verifiee)")

# Q3 — Types d'un individu
print("\n[Q9] Types de 'chef_ducasse' apres raisonnement :")
for t in chef_ducasse.is_a:
    print(f"  ▸ {t}")

print("\n[Q10] Types de 'chef_sara' apres raisonnement :")
for t in chef_sara.is_a:
    print(f"  ▸ {t}")

print("\n[Q11] Types de 'boeuf_bourguignon' :")
for t in boeuf_bourguignon.is_a:
    print(f"  ▸ {t}")

# Q4 — Valeurs de roles
print("\n[Q12] Plats proposes par Le Jules Verne :")
for p in le_jules_verne.propose:
    print(f"  ▸ {p.name}")

print("\n[Q13] Chef(s) employe(s) par La Tour d'Argent :")
for c in la_tour_argent.emploie:
    print(f"  ▸ {c.name}")

print("\n[Q14] Plats prepares par chef_ducasse :")
for p in chef_ducasse.prepare:
    print(f"  ▸ {p.name}")

print("\n[Q15] Ingredients contenus dans boeuf_bourguignon :")
for i in boeuf_bourguignon.contient:
    print(f"  ▸ {i.name}  [type atomique : {type(i).__name__}]")

# Q5 — Instances d'un concept
print("\n[Q16] Toutes les instances de RESTAURANT_GASTRONOMIQUE :")
for r in RESTAURANT_GASTRONOMIQUE.instances():
    print(f"  ▸ {r.name}")

print("\n[Q17] Toutes les instances de CHEF_ETOILE :")
for c in CHEF_ETOILE.instances():
    print(f"  ▸ {c.name}")

print("\n[Q18] Toutes les instances de PLAT_SIGNATURE :")
for p in PLAT_SIGNATURE.instances():
    print(f"  ▸ {p.name}")

print("\n[Q19] Toutes les instances d'ALLERGEN :")
for a in ALLERGEN.instances():
    print(f"  ▸ {a.name}")

print("\n[Q20] Toutes les instances de RESTAURANT_VEGETARIEN :")
for r in RESTAURANT_VEGETARIEN.instances():
    print(f"  ▸ {r.name}")


# =============================================================================
# SECTION 6 — RECAPITULATIF TBOX / ABOX
# =============================================================================

print("\n" + "=" * 70)
print("  RECAPITULATIF — TBox et ABox")
print("=" * 70)

print("""
┌─────────────────────────────────────────────────────────────────────┐
│  TBox — Terminologie (definitions)                                  │
├──────────────────────────────┬──────────────────────────────────────┤
│  Concept Defini              │  Definition (DL)                     │
├──────────────────────────────┼──────────────────────────────────────┤
│ RESTAURANT_GASTRONOMIQUE     │ RESTAURANT                           │
│                              │   ⊓ ≥1 emploie.CHEF                 │
│                              │   ⊓ ≥5 propose.PLAT                 │
│                              │   ⊓ ≥1 possede.CERTIFICATION        │
├──────────────────────────────┼──────────────────────────────────────┤
│ RESTAURANT_ETOILE            │ RESTAURANT_GASTRONOMIQUE             │
│                              │   ⊓ ∃possede.ETOILE_MICHELIN        │
├──────────────────────────────┼──────────────────────────────────────┤
│ RESTAURANT_BISTRONOMIQUE     │ RESTAURANT                           │
│                              │   ⊓ ¬(∃possede.CERTIFICATION)       │
├──────────────────────────────┼──────────────────────────────────────┤
│ RESTAURANT_VEGETARIEN        │ RESTAURANT                           │
│                              │   ⊓ ∀propose.(PLAT                  │
│                              │      ⊓ ¬∃contient.VIANDE)           │
├──────────────────────────────┼──────────────────────────────────────┤
│ RESTAURANT_RAPIDE            │ RESTAURANT ⊓ ≤3 propose.PLAT        │
├──────────────────────────────┼──────────────────────────────────────┤
│ CHEF_ETOILE                  │ CHEF                                 │
│                              │   ⊓ ∃prepare.PLAT                   │
│                              │   ⊓ ∃possede.CHEF_CERTIFIE          │
├──────────────────────────────┼──────────────────────────────────────┤
│ PLAT_SIGNATURE               │ PLAT                                 │
│                              │   ⊓ ∃contient.PRODUIT_LOCAL         │
│                              │   ⊓ ≥1 accompagne.BOISSON           │
├──────────────────────────────┼──────────────────────────────────────┤
│ DISJONCTION                  │ RESTAURANT_GASTRONOMIQUE             │
│                              │   ⊓ RESTAURANT_RAPIDE ≡ ⊥           │
└──────────────────────────────┴──────────────────────────────────────┘
""")

print("""
┌─────────────────────────────────────────────────────────────────────┐
│  ABox — Assertions (instances et roles)                             │
├───────────────────────┬─────────────────────────────────────────────┤
│  Individu             │  Type assert                                │
├───────────────────────┼─────────────────────────────────────────────┤
│ le_jules_verne        │ RESTAURANT_ETOILE                           │
│ la_tour_argent        │ RESTAURANT_GASTRONOMIQUE                    │
│ chez_omar             │ RESTAURANT_BISTRONOMIQUE                    │
│ mcdonalds             │ RESTAURANT_RAPIDE                           │
│ le_jardin_vert        │ RESTAURANT_VEGETARIEN                       │
│ chef_ducasse          │ CHEF_ETOILE                                 │
│ chef_robuchon         │ CHEF_ETOILE                                 │
│ chef_sara             │ CHEF  (pas etoile : pas de certification)   │
│ boeuf_bourguignon     │ PLAT_SIGNATURE                              │
│ couscous_royal        │ PLAT                                        │
│ burger_vegan          │ PLAT                                        │
│ truffe                │ PRODUIT_LOCAL ⊑ INGREDIENT                 │
│ lactose               │ ALLERGEN      ⊑ INGREDIENT                 │
│ etoile_michelin       │ ETOILE_MICHELIN ⊑ CERTIFICATION            │
│ cert_ducasse          │ CHEF_CERTIFIE   ⊑ CERTIFICATION            │
└───────────────────────┴─────────────────────────────────────────────┘

  Assertions de roles :
  emploie(le_jules_verne,       chef_ducasse)
  propose(le_jules_verne,       boeuf_bourguignon, tarte_tatin,
                                soupe_tomate, salade_nicoise, couscous_royal)
  possede(le_jules_verne,       etoile_michelin)
  emploie(la_tour_argent,       chef_robuchon)
  possede(la_tour_argent,       label_bio)
  emploie(chez_omar,            chef_sara)
  propose(chez_omar,            couscous_royal)
  propose(mcdonalds,            burger_vegan)
  prepare(chef_ducasse,         boeuf_bourguignon, tarte_tatin)
  possede(chef_ducasse,         cert_ducasse)
  prepare(chef_robuchon,        soupe_tomate, salade_nicoise)
  possede(chef_robuchon,        cert_robuchon)
  prepare(chef_sara,            couscous_royal)
  contient(boeuf_bourguignon,   truffe)
  accompagne(boeuf_bourguignon, vin_bordeaux)
  contient(couscous_royal,      agneau, pois_chiche)
""")

print("=" * 70)
print("  FIN DU TP 5")
print("=" * 70)

# Sauvegarde OWL
onto.save(file="restauration_ontologie.owl", format="rdfxml")
print("\n  Ontologie sauvegardee → restauration_ontologie.owl")