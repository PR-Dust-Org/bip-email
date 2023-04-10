+ Find a few queries to test on a 14-day scope
  - "Montant de ma dernière course de taxi"
	- sujet résolution date & "dernière" qui marche pas avec le map reduce? ou alors moins bien
  - "3 derniers appartements proposés par belles demeures"
	- "proposés par belles demeures" ça va marcher?
  - "horaires de mon train pour vannes"
  - "horaires de mon train pour Avignon" -> you don't have that in your mail
  - OPT - very hard: "horaires du train pour belle ile"
+ Fais marcher la query "horaires de mon train pour vannes"
  - la sem search doit contenir le chunk; checke si ça marche
  - regarde les docs que te sors la sem search
  - les 5 docs en input d'une dust app
  - qui prompt gpt4 en map-reduce
  - puis fédère les résultats
- Fais marcher les 3 autres
  - Debug montrant temps de la query
  - debug montrant sujet/date/similarité de chaque chunk retenu
  - cas uber
	- déterminer la valeur de similarité recherchée V
	- règle de cutoff de similarity: binary search until 1 < S < 10

	- binary search pour avoir > 1


## Later on 
- inclus un lien vers les emails dans la réponse
- Trouve 10 nouvelles queries et décide comment les gérer
  - 80/20, et SURTOUT ne pas faire plus que 80
- Gère le cas du chat "simple", différencie avec l'analytics
- Interface de chat de test (local)
- Chat sur whatsapp
- Audit de vitesse
  - Essayer avec 3.5-turbo pour aller + vite? ou davinci-003?

# Maybe
- refactor email_batches function to be cleaner
- refactor chunks to return a list of objects rather than two lists of str and dict

# Done
+ Email retrieval script
  - store in cloud DB
  	+ pick right DB, setup git
	+ test pinecone access
	+ write e2e test with your emails from date X (more than 50 messages)
		+ on a test index
		+ fetch a few message ids
		+ do semantic search for one query and get it back properly
	- implement retrieval
		+ refactor store (name, function outputs)
		+ implement chunk_id
		+ email_batches
		+ _store_email_batch
		+ document the assumption that messages are sorted by internaldate descending => means it's fine to stop
		
+ command-line usage
+ Store 2 weeks in the DB (incl. most recent)
  + update logging so you know where you are
  + check that already stored mail is not stored again (write the test)
  - run for 2 weeks
