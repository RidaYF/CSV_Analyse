README - Analyseur de Fichiers CSV avec Dash

Structure du projet
    app.py : Le fichier principal de l'application. Contient le code pour lancer le serveur Dash et gérer l'interface utilisateur.
    firebase_configuration.py : Configure Firebase pour le stockage et la récupération des données.
    private_key_of_database.json : Clé privée pour accéder à votre base de données Firebase (gardez ce fichier confidentiel).
    utils.py : Contient des fonctions utilitaires réutilisables dans le projet.
    graph_types.py : Définit différents types de graphiques utilisés dans l'application.
    assets/ : Contient les fichiers statiques (CSS, images, etc.) utilisés par Dash.
    CSV FILES/ : Dossier pour stocker les fichiers CSV que l'utilisateur souhaite analyser.
    pycache/ : Dossier généré automatiquement par Python, contenant les fichiers compilés.

Bibliothèques et dépendances
Standard Libraries
    base64, io, os, tempfile, re

External Libraries
    dash, dash-bootstrap-components, plotly
    pandas
    flask-caching
    reportlab
    firebase_admin
    bcrypt

Installation des dépendances:
pip install dash dash-bootstrap-components pandas flask-caching reportlab plotly bcrypt firebase_admin
pip install -U kaleido

Utilisation (sans docker)
1. Pré-requis
    Installez Python 3.8+.
    Installez toutes les dépendances nécessaires (voir ci-dessus).

2. Lancer l'application 
    Placez les fichiers CSV dans le dossier CSV FILES.
    Exécutez le fichier app.py :
    python app.py
    Accédez à l'application via votre navigateur à l'adresse : http://127.0.0.1:8050.

Lancement d'application en utilisant Docker:
    1-Accédez au fichier d'application avec Terminal du Docker.
    2-executer cette commande pour créer une image pour l'application: docker build -t docker_csv_project .
    3-lancer l'application avec la commande: docker run -p 8050:8050 docker_csv_project


Firestore Firebase de base de données
    vouz pouvez voir la base de données par suivre les étapes suivantes:
        Rediriger vers ce lien: https://console.firebase.google.com/u/0/
        Connecter avec ce compte g-mail: e-mail: csv.graph.test@gmail.com  password: csvtest123
        choisir le projet: Graph CSV
        A gauche au side bar cliquer sur Firestore Database
    vouz allez trouver une collection de données (table de données) des utilisateurs

Un compte pour login à la page d'accueil d'application(si vous ne voulez pas créer un):
    Username: mgsi
    Password: mgsi123

Test des fichiers CSV
    on a ajouter un dossier "CSV FILES" qui contient des fichiers pour tester les fonctionnalités d'application

Auteurs : 

    [ Yassine Tabakna - Ilays Hrizi - Hajar Lamghari 3chirt simo- Yassine Ait Bouhou ]
