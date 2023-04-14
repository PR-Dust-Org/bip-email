## Todo now
- Créer une base de test queries que je peux refaire tourner facilement
  - command-line "test-queries"
  - 10 queries
  - envoi à un LLM query, answer, expected_data_in_answer => qui renvoie Y/N
  - calcul du score total et envoi du score + les failures avec le détail
- Expérimenter sur 4-5 emails le résumé de threads: on ne perd pas d'infos?
  - comment va-t-on générer le résumé?
  - 3 emails clefs sur 3 queries clefs : horaires train, mail françois?
  - + 2 long threads (et imaginer des queries)
  - script python pour les récupérer, les résumer et afficher le résumé
- Code pour segmenter par threads dans le retriever
  - possibilité d'avoir plusieurs bases donc
  - en metadata non indexée, full thread + résumé
- Segmentation d'1 mois, test pour les queries concernées
# Milestone 2 pour bip email
#### Misc
+ regénération du token gmail
+ logging
#### Amélioration de la qualité
- queries : plus de queries marchent
  - "le dernier", "le prochain" + celles de la liste => > 80%
  - fonctionnement sur 1 an et demi
- uses case: résume les derniers messages (le thread)
- use case: résume un lien que je te partage (bonus)
- small chat: réponds à des follow-up questions
- (OPT) vitesse : < 10s most of the time
  - fais un audit et vois de combien tu peux raisonnablement baisser sans hoster ton modèle

#### Install pour d'autres personnes
- secrets handling
- ajout d'une autre pers. dans le code
- possibilité d'avoir d'autres indexes emails
- gestion des credentials pour une autre personne
- script d'install pour une autre personne
- script de retrieve qui tourne toutes les heures


# Brainstorm Milestone 2
En soirée avec des inconnus? ou peinard avec lapinette, shokooh, sam...
=> Peinard (sinon trop fat)
Caveats à expliquer aux gens:
- sur 1 an pour l'instant
- à jour de 1h sur tes emails
- c'est pas une barre de search, c'est une pers à qui tu parles -- résister à la search query

Car en parallèle il faut que moi j'utilise, et pour ça améliorer


### Liste des features requises
#### Amélioration de la qualité
- queries : plus de queries marchent
  - "le dernier", "le prochain" et la liste de tous les autres
- uses case: résume les derniers messages (le thread)
- small chat: réponds à des follow-up questions
- vitesse : < 10s most of the time

#### Install pour d'autres personnes
- regénération du token gmail ok
- secrets handling
- ajout d'une autre pers. dans le code
- possibilité d'avoir d'autres indexes emails
- gestion des credentials pour une autre personne
- script d'install pour une autre personne
- script de retrieve qui tourne toutes les heures





### Idées techniques
- utiliser un thread entier VS un chunk de message quand c'est pertinent
- cosine distance aml précision
- vitesse: 
  - n'analyser qu'un texte quand un seul suffit? 
  - enlever la passe de construction de question?
  - diviser la longueur des textes générés demandés?
  - résumer les threads entiers, et utiliser ça comme embeddings - ainsi on se limite à des textes plus courts et denses en infos
  - 2 étapes - fast search, puis prévenir si fail et longer search then (<10s, > 1mn)

### Liste des features possibles
- auth flow via whatsapp + script qui fait le retrieve  
# Legacy - TBS
Objectif: 
1- Montrer à mes amis - regardez comme c'est cool
2- projet opensource utilisable par d'autres - sur mzero, twitter et linkedin



## Milestone 1
- 5 queries sur 10 (sur une base de ~30 queries dont 10 adversariales)
  - créer la base de 30 queries (= 15 queries avec 2* formulations), en jsonl
  - exécuter et sortir le score
- Vitesse: moins de 10s dans 80% des cas, jusqu'à 30s dans 95% des cas avec message intermédiaire à 10 & 20s (je cherche... je cherche encore :emo-sorry:) 
  - l'exécution doit sortir les métriques correspondantes
- Montrable via whatsapp aux autres, et noter combien veulent tester
  - permettre l'utilisation whatsapp durable (sans token renew)
  - ajouter la lambda python qui fait le taf susdécrit, les brancher

## Publication
- Installation simple 
  - google auth flow par user
- Installation différenciée regular user VS dev 
  - clef OAI individuelle + pinecone db account for devs -- and it's free
  - fully managed for regular users - and it's free for now but limited to 100 users (since I pay for the cost of hosting, database & openai api calls...)
- Gif de démo
- français & anglais


## Milestone 2
- Tu installes toi même pour les autres en envoyant les infos par chat
  - ça te renvoie le lien pour l'auth flow
  - puis un index pinecone est créé et le storage commence
