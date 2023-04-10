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
