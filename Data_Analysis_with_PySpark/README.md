# PySpark + JupyterLab + Delta Lake (Docker)

## Versions retenues

- Python 3.12
- Java 17
- Apache PySpark 4.2.0
- Delta Lake `delta-spark` 4.4.1
- JupyterLab 4.4.5

`delta-spark==4.4.1` accepte PySpark `>=4.0.1,<=4.2.0`. N'utilisez donc pas `pyspark==4.3.0` avec cette version de Delta.

## Prérequis

- Docker Desktop installé et démarré (Windows/macOS) ou Docker Engine + Compose (Linux).
- Dans Docker Desktop, allouer idéalement 4 CPU et 6 Go de RAM au conteneur.
- Aucun Java/Python/Spark n'est à installer sur l'hôte : ils sont dans l'image.

## Démarrer

Dans un terminal, placez-vous dans ce dossier :

```bash
docker compose build
docker compose up -d
docker compose logs -f
```

Ouvrez ensuite http://localhost:8888 et saisissez le token `pyspark-local`.

Pour personnaliser le token, copiez `.env.example` vers `.env`, modifiez sa valeur, puis relancez :

```bash
docker compose down
docker compose up -d
```

## Arrêter / redémarrer

```bash
docker compose down
docker compose up -d
```

Les notebooks, données et tables Delta sont conservés sur l'hôte dans `notebooks/`, `data/` et `warehouse/`.

## Test PySpark + Delta

Ouvrez `notebooks/00_test_pyspark_delta.ipynb` et exécutez les cellules dans l'ordre.
Le notebook crée une table Delta dans `/workspace/warehouse/demo_delta`.

## Vérifier les versions depuis un notebook

```python
import sys
import pyspark
import delta

print("Python:", sys.version)
print("PySpark:", pyspark.__version__)
print("Delta:", delta.__version__)
```

## Dépannage

- Si le port 8888 est occupé, remplacez le côté gauche de `8888:8888` par `8889:8888`, puis ouvrez `http://localhost:8889`.
- Pour voir les logs : `docker compose logs -f pyspark-jupyter`.
- Pour reconstruire après une modification de `requirements.txt` : `docker compose build --no-cache`.
- Pour supprimer le conteneur : `docker compose down`. Ne supprimez pas les dossiers `data/`, `notebooks/` ou `warehouse/` si vous voulez garder votre travail.

Cette configuration utilise Spark en mode local (`local[*]`) : c'est idéal pour apprendre sur une seule machine, pas un cluster distribué de production.
