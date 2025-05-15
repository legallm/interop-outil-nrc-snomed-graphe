# Snomed_graphe

## À propos du projet 
Un projet Python pour manipuler la SNOMED CT sous forme de graphe.

Ce projet est un fork de [snomed_graph](https://github.com/VerataiLtd/snomed_graph) visant à ajouter les fonctionnalités suivantes :
- Distinguer les termes préférés (PT) des synonymes acceptables (SYN)
- Permettre de gérer différentes langues
- Permettre de créer des sous-graphes

Ce projet ne supporte pas l'ECL (Expression Constraint Language), et ne doit pas être considéré comme un remplacement pour un serveur de Terminologie. L'objectif principal de ce projet est de faciliter les cas d'usage d'analyse de données ou de machine learning.

Le projet a 3 dépendances : 
- `networkx` - N'importe quelle version >= 3.0 devrait fonctionner.
- `pandas`.
- `tqdm`.

## Installation du projet
```shell
# Exemple avec le gestionnaire d'environnement venv
python3 -m venv ~/.venv/mon_env
source ~/.venv/mon_env/bin/activate

# Récupérer le projet
git clone git@github.com:legallm/interop-outil-nrc-snomed-graphe.git
cd ./interop-outil-nrc-snomed-graphe/
pip install .
```

## Licence
Sous licence Apache 2.0, voir le fichier [LICENSE](https://github.com/ansforge/interop-outil-nrc-import-batch-ftcg/blob/master/LICENSE.md) pour plus d'informations.

## Remerciements
- [https://github.com/VerataiLtd/snomed_graph](https://github.com/VerataiLtd/snomed_graph)