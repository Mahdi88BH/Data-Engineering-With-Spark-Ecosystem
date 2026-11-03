# Delta Lake + PySpark + JupyterLab (Docker)

Environnement local d'apprentissage pour Windows + Docker Desktop.

## Prérequis

1. Windows 10/11.
2. Docker Desktop installé et démarré (mode Linux containers).
3. Virtualisation activée dans le BIOS/UEFI.
4. Dans Docker Desktop, prévoir idéalement 4 CPU et 6 Go de RAM pour commencer.

Aucune installation locale de Java, Python, Spark ou Delta Lake n'est nécessaire.

## Démarrage

Ouvrez PowerShell dans le dossier du projet :

```powershell
docker compose build
docker compose up -d
docker compose logs -f
```

Ouvrez ensuite :

- JupyterLab : http://localhost:8888
- Token par défaut : `deltalake`

Pour personnaliser le token, copiez `.env.example` vers `.env`, puis modifiez `JUPYTER_TOKEN`.

## Notebook de démarrage

Dans JupyterLab, ouvrez :

`notebooks/01_delta_lake_fundamentals.ipynb`

Le notebook contient :
- création d'une SparkSession configurée pour Delta Lake ;
- création et lecture d'une table Delta ;
- inspection de l'historique ;
- UPDATE, DELETE et MERGE ;
- Time Travel.

Les JARs Delta compatibles sont téléchargés par `configure_spark_with_delta_pip` lors de la première création de SparkSession. Une connexion Internet est donc nécessaire au premier lancement de Spark.

## Commandes utiles (PowerShell)

```powershell
# Démarrer
docker compose up -d

# Voir les logs
docker compose logs -f

# Arrêter sans supprimer les données
docker compose down

# Reconstruire après modification du Dockerfile ou requirements.txt
docker compose down
docker compose build --no-cache
docker compose up -d

# Ouvrir un shell dans le conteneur
docker compose exec delta-notebook bash
```

Les notebooks sont dans `./notebooks` et les tables Delta dans `./data` sur Windows : les fichiers restent donc disponibles après l'arrêt du conteneur.

## Dépannage

- Si le port 8888 est déjà utilisé, remplacez `"8888:8888"` par `"8889:8888"` dans `docker-compose.yml`, puis ouvrez http://localhost:8889.
- Si Docker manque de mémoire, augmentez la mémoire allouée à Docker Desktop ou réduisez le nombre de partitions dans vos exercices.
- Si Spark ne télécharge pas les dépendances Delta, vérifiez l'accès Internet du conteneur puis redémarrez le kernel Jupyter.
- Pour repartir de zéro, arrêtez le conteneur et supprimez manuellement le contenu du dossier `data` (attention : cela supprime vos tables Delta).

## Versions épinglées

- Python 3.11
- Java 17
- Apache Spark / PySpark 4.0.0
- Delta Lake 4.0.0

Delta Lake 4.0.0 est compatible avec Spark 4.0.x. Consultez la matrice officielle avant de modifier ces versions.
