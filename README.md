# Datascientest: projet New York Times


## Contexte 
Le projet a été réalisé dans le cadre du bootcamp Data Engineer proposé par [Datascientest et l'Ecole des Mines ParisTech](https://datascientest.com/formation-data-engineer). 

L'équipe qui à réalisé le projet se compose de:
* Anna Temerko: [Github](https://github.com/anna-tem) / [Linkedin](https://www.linkedin.com/in/anna-temerko-688467200/)

* Mathieu Lefebvre: [Github](https://github.com/MathieuLefebvre) / [Linkedin](https://www.linkedin.com/in/mathieulefebvre/)

* Edouard Philippe: [Github](https://github.com/ep2207) / [Linkedin](https://www.linkedin.com/in/edouard-philippe-84ab53180/)

* Cédric Soares: [Github](https://github.com/cedricsoares) / [Linkedin](https://www.linkedin.com/in/csoares/)

Il nous a été demandé de réaliser un projet permettant de mettre en oeuvre un large pannel de compétences du métier de Data Engineer. 

Ce projet devait utiliser comme source de données les API du [portail développeur du New York Times](https://developer.nytimes.com).

Il nous a été laissé la liberté de la finalité du projet et de la stack technique mise en oeuvre. 

## Notre proposition 

Notre équipe a décidé de réaliser un ensemble de services dont la finalité est un dashboard permettant de suivre les contenus produits par les équipes du New York Times. 

L'utilisateur que nous avons retenu est un rédacteur en chef du titre qui souhaite suivre la production journalistique et identifier des tendances dans :

* Les articles relatifs aux news

* Les listes thématiques de livres best sellers

* Les chroniques de films 

## Contraintes du projet 

* Les contraintes des API du New York Times:
    * 60 appels maximum par minute
    * 500 appels maximum par jour

* Un projet devant être réalisé en 1.5 mois


## La solution technique 

### Vue globale 

![Schéma Global](https://drive.google.com/uc?id=15eTb-tRUYqv3saPNhLksQ0Vr4LIn_EwF) 

La solution proposée se compose de : 

* Un ETL qui a la charge de récupérer les contenus du New York Times.

* Une base de données Elasticsearch où son entreprosés les documents récupérés.

* Un dashboard Dash.

* Une API FastApi permettant au dashboard de requêter la base de données.

* Un DAG Airflow pour gérer l'orchestration de l'ETL

### Stack technique du projet 

![Stack Technique](https://drive.google.com/uc?id=1RYbTblEa8fZXzOX_oNVWpPzepTTtjXR_)

### L'ETL

#### Digramme de fonctionnement 

![Diagramme de fonctionnement](https://drive.google.com/uc?id=1VLkzxuwBknjf3FcdmaFbJ1QpSV3p4tid)

### La base de données Elasticsearch

#### Les spécications

Nous avons implémenté trois index :
 
* news

* books 

* movies 

Chaque index utilise les settings suivants :

* 2 chards

* 2 réplicats 

* Un analyseur `English` sur tous les champs texte


### Structuration des routes de l'API et des graphiques du dashboard 

![Tableau de board API - Dashboard](https://drive.google.com/uc?id=11elwT33eSY_XH-4XriE8Jcf3a1ynjJTj)


#### Le dashboard

![Dashboard](https://drive.google.com/uc?id=1qBCBidKy6U8DVcGVJs_2AmQXwltjkzKb)


#### L'API 

![Screenshot de l'Api](https://drive.google.com/uc?id=1ZLY2V5RMm2VQPuoKgnDo-zmLlAdOUicq)


### Le DAG 

![DAG Airflow](https://drive.google.com/uc?id=18fLo_6Xlawg_30dmAtBdmlRzfqhnb90e)

Le DAG réalise deux taches:

* Vérifier que la base de données Elasticsearch est bien fonctionelle

* Si c'est le cas lancer l'ETL

Le DAG envoie des alertes sur le groupe Slack de l'équipe en cas de succès ou de l'échec de chaque tâche.


## Le repository

```
.
├── README.md
├── api
│   ├── Dockerfile
│   ├── __init__.py
│   ├── logs
│   ├── main.py
│   ├── requirements.txt
│   └── start.sh
├── dag
│   └── etl_dag.py
├── dash
│   ├── Dockerfile
│   ├── __init__.py
│   ├── assets
│   ├── dashboardLists.py
│   ├── main.py
│   ├── queries.py
│   ├── requirements.txt
│   └── start.sh
├── data
│   ├── _state
│   ├── indices
│   ├── node.lock
│   ├── nodes
│   └── snapshot_cache
├── docker-compose.yml
├── etl
│   ├── Dockerfile
│   ├── __init__.py
│   ├── app.py
│   ├── constants.py
│   ├── extract.py
│   ├── load.py
│   ├── logs
│   ├── requirements.txt
│   ├── session.py
│   ├── start.sh
│   ├── transform.py
│   └── utils.py
├── logs
│   ├── api
│   ├── dash
│   └── etl
├── notebooks
│   ├── ES_load.ipynb
│   ├── api results
│   ├── api_exploaration.ipynb
│   ├── books_queries.ipynb
│   ├── movies_queries.ipynb
│   └── news_queries.ipynb
└── requirements.txt
```

En plus du code des services, le repository contient une series de notebooks ayant servi :

* À découvrir les API du New York Times 

* À élaborer la logique de l'ETL

* À construire les requêtes Elasticsearch utilisées dans l'API


## Mode d'emploi 

* Hormis le DAG l'ensemble des services se lance avec la commande

    ```
    docker-compose up -d
    ```

* Le fichier du code du DAG doit être mis dans le dossier `DAG` d'une configuration Airflow locale. Celle-ci doit avoir accès à l'API Docker sur le poste où elle est lancée. Deux variables d'environement sont à paramétrer:

    * `local_logs`: Le chemin d'accès absolu du fichier `logs` dans le dossier du projet clonné
    * `network_id`: L'identifiant du network docker `ny_times_backend`. Ce dernier est retrouvable en utilisant la commande suivante:

        ```
        docker network ls
        ``` 

    Les alertes Slack nécessitent de créer un webhook sur la plateforme de paramétrer une une connexion dans Airfflow. Le code des alertes est déjà implémenté dans le DAG. [L'article Chris Young publié sur Towards Data Science](https://towardsdatascience.com/automated-alerts-for-airflow-with-slack-5c6ec766a823) indique comment réaliser le paramétrage.

    Avant d'activer le DAG il est également nécessaire d'enregistrer une API Key sur le portail développeurs du New York Times dans un fichier `.env`. Ce dernier sera aussi nécessaire afin d'utiliser les notebooks d'exploration. Le fichier sera a ranger dans chacun de ces dossiers `etl` et `notebooks`. La démarche pour récupérer l'API KEY est indiquée ci-dessous. 


    ### Paramétrage de l'API New York Times Developer
    1. créer un compte sur la plateforme [New York Times Developers](https://developer.nytimes.com)
    2. Suivre les instruction de la page [*Get Started*](https://developer.nytimes.com/get-started) pour récupérer une clé API
    3. Créer un fichier `.env` à la racine du dossier local où le projet a été créé et ajouter votre clé API de la manière suivante :
    ```
    API_KEY=<API_KEY_NYT_DEVELOPER>
    ```
