# Documentation technique sur la collection de données sans internet

> on va utiliser le capteur NDIR CO2 par exemple

## Schéma Global

Le problème posé dans le code c’est qu’il envoie directement à l’InfluxDB, mais il ne vérifie pas que si la connexion est établi ou pas. Cela risque de perdre les données collectées.

![schema avant](https://drive.google.com/uc?id=0B_jq0BJo4ikCd3dGSk1ETU5qWkk)

La solution que je propose est d’établir un dépôt local qui conserve les données, il va vérifier chaque fois la connexion avant il envoie les données au serveur.

![schema apres](https://drive.google.com/uc?id=0B_jq0BJo4ikCNlp2dFpMemZ1dVE)

Raspberry Pi 2 va conserver les données dans un fichier texte sous forme de « line Protocol». Il n’y a pas de façon prédéfinie pour vérifier la connexion, mais on peut également consulter la page d’accueil d’InfluxDB pour la vérifier. Après la vérification, il envoie les données et supprime le fichier local.

La fonction *run()* va utilise *sense_into_file()* et write_from() au lieu de utilise sense().

## Calcule simple de stockage local

1 Jour = 86,400 secondes

Si on utilise la fréquence par défaut (10 secondes), il collecte 8640 lignes de données dans un jour.
Une ligne de données dépense presque 90 octets. Cela fait 777,600 octets, c’est-à-dire 759,4 Ko par jour.


## fonction référence

> sense_into_file(self)

Cette fonction va récupérer les données de capteur, et après appelle la fonction write_into_file pour ajouter les données dans le fichier.

> write_from(self, directory_path, db=”apolline”)

Cette fonction va enregistrer les données dans la BD. Quand les données sont enregistrées, les fichiers locaux sont supprimés.

> connection_established(self)

Cette fonction va faire une requête GET pour vérifier la connexion est bien établie.

> name_file(cardinal, date=datetime.datetime.now().strftime("%Y%m%d")

Cette fonction va nommer le ficher selon le date et la cardinalité. Exemple : 20170125N01.txt

> line_number_of_file(file)

Cette fonction va calculer le nombre de lignes en saisisant le fichier.

> write_into_file(directory_path)

Cette fonction va contrôler les opérations de fichier. Quand il n’y a pas de fichier pour aujourd’hui, il en crée un ; S’il y a un fichier qui ne dépasse pas 4000 lignes aujourd’hui, on ajoute les données dedans ; Sinon ; on crée un nouveau fichier.
