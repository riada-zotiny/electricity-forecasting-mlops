Suivi – electricity-forecasting-mlops

Objectif : pipeline MLOps de bout en bout pour prévoir la consommation électrique française (RTE éCO2mix + météo). Stack : Python, Polars, DuckDB, Airflow, Pandera, XGBoost, statsmodels, MLflow, FastAPI, Docker, Evidently.

Étape 0 – Mise en place
[ ] Cloner le repo et créer l'arborescence (src/, dags/, tests/, notebooks/, data/, docker/)
[ ] Environnement Python (uv ou poetry) + pyproject.toml
[ ] Pre-commit : ruff, black, mypy
[ ] docker-compose.yml avec Airflow (et Postgres pour Airflow)
[ ] Premier commit propre + README avec objectif du projet
Étape 1 – Exploration des données
[ ] Télécharger l'historique éCO2mix (consommation nationale ou par région)
[ ] Récupérer la météo (Open-Meteo : température, au même pas de temps)
[ ] Notebook d'exploration : tendances, saisonnalités (jour, semaine, année), trous, valeurs aberrantes
[ ] Repérer les pièges : changements d'heure, jours fériés, doublons, pas de temps irrégulier
[ ] Noter les constats dans le README
Étape 2 – Ingestion et nettoyage
[ ] Script d'ingestion (API ou fichiers) écrit en module Python, pas en notebook
[ ] Stockage brut en Parquet (couche raw)
[ ] Nettoyage avec Polars : types, fuseau horaire, doublons, interpolation des trous courts
[ ] Jointure consommation + météo
[ ] Requêtes d'analyse avec DuckDB sur les Parquet
[ ] Tests unitaires (pytest) sur les fonctions de nettoyage
Étape 3 – Qualité des données
[ ] Schéma Pandera (types, plages de valeurs, non-null)
[ ] Contrôles de fraîcheur (dernière date reçue) et de complétude (% de trous)
[ ] Rapport de qualité sauvegardé à chaque run
[ ] Le pipeline s'arrête ou alerte si un contrôle échoue
Étape 4 – Orchestration Airflow
[ ] DAG quotidien : ingestion → nettoyage → contrôles qualité → features
[ ] Gestion des reprises (retries) et du backfill
[ ] Tâches idempotentes (relancer un jour ne crée pas de doublons)
[ ] Logs clairs pour chaque tâche
Étape 5 – Modélisation séries temporelles
[ ] Features : lags, moyennes glissantes, heure, jour, mois, jours fériés, température
[ ] Baseline naïve (même heure la veille / la semaine passée)
[ ] Modèle statistique : SARIMA (statsmodels)
[ ] Modèle ML : XGBoost
[ ] Validation temporelle (backtesting en fenêtre glissante, pas de split aléatoire)
[ ] Métriques : MAE, RMSE, MAPE + graphiques prévu vs réel
[ ] Tableau comparatif des modèles dans le README
Étape 6 – Suivi des expériences
[ ] Serveur MLflow dans docker-compose
[ ] Logger paramètres, métriques et artefacts de chaque entraînement
[ ] Enregistrer le meilleur modèle dans le Model Registry
[ ] DAG de réentraînement planifié (hebdomadaire)
Étape 7 – Déploiement
[ ] API FastAPI : endpoint /predict et /health
[ ] Chargement du modèle depuis le registre MLflow
[ ] Dockerfile de l'API
[ ] Tests de l'API
Étape 8 – Monitoring
[ ] Dérive des données (Evidently) entre la période d'entraînement et les nouvelles données
[ ] Suivi de la performance réelle quand les vraies valeurs arrivent
[ ] Réentraînement déclenché si la performance baisse sous un seuil
Étape 9 – CI/CD et finitions
[ ] GitHub Actions : lint + tests à chaque push
[ ] Build de l'image Docker dans la CI
[ ] README final : schéma d'architecture, comment lancer, résultats, choix techniques
[ ] Topics GitHub : mlops, airflow, time-series, xgboost, mlflow
[ ] Préparer 2-3 phrases pour présenter le projet en entretien