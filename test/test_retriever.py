import datetime
import unittest

from bip.email import retriever


class MyTestCase(unittest.TestCase):
    def retrieve_emails(self, test_retriever):
        test_retriever._index.delete(delete_all=True)
        test_retriever.update_email_index(
            datetime.datetime(2023, 3, 28, 0, 0, 0),
            datetime.datetime(2023, 3, 30, 0, 0, 0))

    def test_retrieval(self):
        # retrieve mails between 2023-03-28 and 2023-03-30
        test_retriever = retriever.Retriever('test', '../secrets')
        self.retrieve_emails(test_retriever)
        # Message id test
        result = test_retriever._index.fetch(
            ids=["1872c13dd549e130-0"],
            namespace="test")
        self.assertEqual(
            result['vectors']['1872c13dd549e130-1']['metadata']['subject'],
            'Ton soutien peut faire la différence')

        # semantic search test
        query = test_retriever._embeddings.embed_query(
            text="Entreprise de bijoux, luxe et joaillerie")
        result = test_retriever._index.query(
            top_k=3,
            vector=query,
            includeValues=False,
            includeMetadata=True,
            namespace="test").get('matches')

        # for each result, assert the value of the subject
        self.assertEqual(result[0].metadata['subject'], 'Gens de Confiance vous présente « Ce jour où... » avec Gemmyo')
        self.assertEqual(result[1].metadata['subject'], 'De nouveaux biens de prestige pour votre recherche')
        self.assertEqual(result[2].metadata['subject'], 'De nouveaux biens de prestige pour votre recherche')


if __name__ == '__main__':
    unittest.main()
