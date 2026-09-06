"""
Géocodage des cantons de baseTogo (Le Togo / localite-togo)
=============================================================

Ce script :
1. Lit index.html et extrait chaque canton unique (région, préfecture, canton).
2. Interroge Nominatim (OpenStreetMap) pour obtenir lat/lon, à raison de
   1 requête/seconde MAXIMUM (politique d'usage Nominatim).
3. Sauvegarde les résultats au fur et à mesure dans cache_coords.json,
   pour pouvoir reprendre le script s'il est interrompu (pas besoin de
   tout relancer depuis zéro).
4. À la fin, écrit index_avec_coords.html : une copie d'index.html où
   chaque entrée baseTogo reçoit deux champs lat / lon.
5. Liste dans cantons_introuvables.json les cantons que Nominatim n'a
   pas su localiser (comme tes lignes "// commune par défaut - à vérifier",
   à corriger manuellement si besoin).

Utilisation :
    pip install requests
    python geocoder_cantons.py

Respecte la politique Nominatim (https://operations.osmfoundation.org/policies/nominatim/) :
- 1 req/s max
- User-Agent identifiant l'app + un contact
"""

import json
import re
import time
import sys
from pathlib import Path

try:
    import requests
except ImportError:
    sys.exit("Installez d'abord la dépendance : pip install requests")

INDEX_HTML = Path("index.html")
CACHE_FILE = Path("cache_coords.json")
INTROUVABLES_FILE = Path("cantons_introuvables.json")
SORTIE_HTML = Path("index_avec_coords.html")

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
USER_AGENT = "LocaliteTogoApp/1.0 (contact: kossivide8@gmail.com)"
DELAI_ENTRE_REQUETES = 1.1  # secondes ; > 1s pour rester large sous la limite

PATTERN_ENTREE = re.compile(
    r'\{\s*r:\s*"([^"]*)",\s*p:\s*"([^"]*)",\s*c:\s*"([^"]*)",\s*can:\s*"([^"]*)",\s*locs:\s*"([^"]*)"\s*\}'
)


def charger_cache():
    if CACHE_FILE.exists():
        return json.loads(CACHE_FILE.read_text(encoding="utf-8"))
    return {}


def sauver_cache(cache):
    CACHE_FILE.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8")


def geocoder(requete):
    params = {"format": "json", "limit": 1, "q": requete}
    headers = {"User-Agent": USER_AGENT, "Accept-Language": "fr"}
    try:
        rep = requests.get(NOMINATIM_URL, params=params, headers=headers, timeout=10)
        rep.raise_for_status()
        data = rep.json()
        if data:
            return float(data[0]["lat"]), float(data[0]["lon"])
    except Exception as e:
        print(f"  ⚠️  Erreur réseau pour '{requete}': {e}")
    return None


def main():
    if not INDEX_HTML.exists():
        sys.exit("index.html introuvable. Placez ce script dans le même dossier que index.html.")

    contenu = INDEX_HTML.read_text(encoding="utf-8")
    entrees = PATTERN_ENTREE.findall(contenu)
    print(f"{len(entrees)} entrées trouvées dans baseTogo.")

    # Cantons uniques (région, préfecture, canton) -> clé de cache
    cantons_uniques = {}
    for r, p, c, can, locs in entrees:
        cle = f"{r.strip()}|{p.strip()}|{can.strip()}"
        cantons_uniques[cle] = (r.strip(), p.strip(), can.strip())

    print(f"{len(cantons_uniques)} cantons uniques à géocoder.\n")

    cache = charger_cache()
    introuvables = []
    deja = len([k for k in cantons_uniques if k in cache])
    print(f"{deja} déjà en cache, {len(cantons_uniques) - deja} à géocoder.\n")

    for i, (cle, (r, p, can)) in enumerate(cantons_uniques.items(), 1):
        if cle in cache:
            continue

        requete = f"{can}, {p}, Togo"
        print(f"[{i}/{len(cantons_uniques)}] {requete} ...", end=" ")
        coords = geocoder(requete)

        if not coords:
            # Repli : essayer au niveau préfecture seulement
            requete_repli = f"{p}, Togo"
            coords = geocoder(requete_repli)
            if coords:
                print(f"✅ (niveau préfecture) {coords}")
            else:
                print("❌ introuvable")
                introuvables.append({"region": r, "prefecture": p, "canton": can})
                cache[cle] = None
                sauver_cache(cache)
                time.sleep(DELAI_ENTRE_REQUETES)
                continue
        else:
            print(f"✅ {coords}")

        cache[cle] = {"lat": coords[0], "lon": coords[1]}
        sauver_cache(cache)
        time.sleep(DELAI_ENTRE_REQUETES)

    # Écrit les cantons introuvables pour vérification manuelle
    if introuvables:
        INTROUVABLES_FILE.write_text(
            json.dumps(introuvables, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        print(f"\n⚠️  {len(introuvables)} cantons introuvables listés dans {INTROUVABLES_FILE}")

    # Injection des coordonnées dans une copie de index.html
    def remplacer(m):
        r, p, c, can, locs = m.groups()
        cle = f"{r.strip()}|{p.strip()}|{can.strip()}"
        info = cache.get(cle)
        bloc = f'{{ r: "{r}", p: "{p}", c: "{c}", can: "{can}", locs: "{locs}"'
        if info:
            bloc += f', lat: {info["lat"]}, lon: {info["lon"]}'
        bloc += " }"
        return bloc

    nouveau_contenu = PATTERN_ENTREE.sub(remplacer, contenu)
    SORTIE_HTML.write_text(nouveau_contenu, encoding="utf-8")

    reussis = sum(1 for v in cache.values() if v)
    print(f"\n✅ Terminé : {reussis}/{len(cantons_uniques)} cantons géocodés avec succès.")
    print(f"Fichier généré : {SORTIE_HTML}")
    print("Vérifiez-le, puis renommez-le en index.html si tout vous convient.")


if __name__ == "__main__":
    main()
