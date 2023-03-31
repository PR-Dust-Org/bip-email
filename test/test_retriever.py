import unittest
from datetime import datetime
from bip.email import retriever


class MyTestCase(unittest.TestCase):
    def test_something(self):
        # retrieve mails between 2023-03-28 and 2023-03-30
        test_retriever = retriever.Retriever()
        test_retriever._index.delete(delete_all=True)
        test_retriever.update_email_index(
            start_date=datetime.datetime(2023, 3, 28, 0, 0, 0),
            end_date=datetime.datetime(2023, 3, 30, 0, 0, 0))

        # query the index
        query = test_retriever._embeddings.embed_query(text="Comment ça va?")
        result = test_retriever._index.query(top_k=3, vector=query)

        # for each result, assert the value of the subject
        self.assertEqual(result[0].meta['subject'], 'Subject 1')
        self.assertEqual(result[1].meta['subject'], 'Subject 2')
        self.assertEqual(result[2].meta['subject'], 'Subject 3')


if __name__ == '__main__':
    unittest.main()
