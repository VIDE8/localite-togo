# 🇹🇬 Rechercher ma Localité au Togo

Application web (PWA) qui permet de retrouver en quelques secondes la **région, la préfecture, la commune et le canton** d'une localité du Togo.

Elle fonctionne dans le navigateur, s'installe sur le téléphone comme une application, et la recherche marche **même sans connexion**.

## Fonctionnalités

- 🔍 Recherche d'une localité avec suggestions pendant la saisie
- 📍 Affichage de la hiérarchie complète : Région · Préfecture · Commune · Canton
- 🗺️ Bouton **Carte** pour voir la localité sur une carte (nécessite Internet)
- 📤 Bouton **Partager / Copier** pour envoyer le résultat
- 📱 Installable sur téléphone (PWA) et utilisable hors-ligne
- 🇹🇬 Carte du Togo en arrière-plan (5 régions et préfectures, sans noms)

## Contenu du dépôt

| Fichier | Rôle |
|---|---|
| `index.html` | L'application complète : page, style, code et **base de données des localités** |
| `sw.js` | Service worker : gère le cache et le fonctionnement hors-ligne |
| `manifest.json` | Informations de l'application installable (nom, couleurs, icônes) |
| `icon-192.png`, `icon-512.png` | Icônes de l'application |
| `geocoder_cantons.py` | Script Python qui sert à préparer les données des cantons |

## Modifier les données

Les localités sont dans `index.html`, dans la liste `baseTogo`. Une ligne correspond à **un canton** :

```js
{ r: "Kara", p: "Kozah", c: "Kozah 1", can: "LAMA", locs: "Fehing, Sahoudè, Kolidé, ..." },
```

- `r` : région, `p` : préfecture, `c` : commune, `can` : canton
- `locs` : les localités du canton, **séparées par une virgule et un espace**

Règles à respecter :

1. Une seule ligne par canton (même région, préfecture, commune et canton).
2. Pas de doublon de localité dans un même canton.
3. Garder les guillemets et la virgule en fin de ligne.

## Mettre en ligne une nouvelle version

1. Modifier `index.html` (bouton ✏️ sur GitHub), puis **Commit changes**.
2. Ouvrir `sw.js` et **augmenter le numéro de version du cache**. Sans cela, les téléphones gardent l'ancienne version.
3. Attendre une minute que GitHub Pages republie, puis recharger l'application.

## Technologies

HTML, CSS et JavaScript, sans framework. Cartes : [Leaflet](https://leafletjs.com). Hébergement : GitHub Pages.

## Auteur

Projet de **VIDE8**.
