import re
import urllib3
import json
import logging

from bip.email.retriever import Retriever, get_secret_key

DUST_BODY = {"specification_hash":
            "f62afe7eb61d97bf348f6fc20d11c051436cef3caf75e53e33bae589111bd70e",
            "config": {"INTENT_QUESTION":{"provider_id":"openai",
                                        "model_id":"gpt-3.5-turbo",
                                        "use_cache":True},
                    "MODEL_1": {"provider_id":"openai",
                                "model_id":"gpt-3.5-turbo",
                                "use_cache":True},
                    "MODEL": {"provider_id":"openai",
                                "model_id":"gpt-3.5-turbo",
                                "use_cache": True}},
                "blocking": True}


class BipAPI(object):

    _http = urllib3.PoolManager()

    def __init__(self):
        self._retriever = Retriever()

    def _get_relevant_email_chunks(self, question):
        result = (self._retriever
                  .query(question, top_k=4, include_metadata=True)
                  .get('matches'))
        return [result['metadata']['text'] for result in result]

    def retrieve_emails(self, start_date, end_date, clear_vs):
        if clear_vs:
            self._retriever.delete_all_emails()
        self._retriever.update_email_index(start_date, end_date)
        logging.info('Done!')

    @classmethod
    def _call_dust_api(cls, dust_input):
        # create the request headers and payload
        dust_key = get_secret_key("dust")
        url = 'https://dust.tt/api/v1/apps/philipperolet/a2cf4c7458/runs'
        headers = {'Content-Type': 'application/json',
                   'Authorization': f'Bearer {dust_key}'}
        body = {**DUST_BODY, 'inputs': [dust_input]}

        # make the request
        response = cls._http.request(
            'POST', 
            url, 
            body=json.dumps(body).encode('utf-8'), 
            headers=headers)
        return json.loads(response.data.decode('utf-8'))

    @staticmethod
    def _compute_answer(question, relevant_email_chunks):
        dust_input = {
            'texts': relevant_email_chunks,
            'query': question}
        result = BipAPI._call_dust_api(dust_input)
        full_text_answer = result['run']['results'][0][0]['value']['completion']['text']
        return re.split(r'Réponse\W*:\W?', full_text_answer)[1]

    def query_emails(self, question):
        relevant_email_chunks = self._get_relevant_email_chunks(question)
        return self._compute_answer(question, relevant_email_chunks)

    def batch_query_emails(self, question_list):
        with open(question_list, 'r') as f:
            questions = [json.loads(line)['question'] for line in f]
        return '\n---\n'.join([self.query_emails(question) for question in questions])

    def gen_test_data(self, query_list):
        with open(query_list, 'r') as f:
            queries = [json.loads(line)['question'] for line in f]
        for query in queries:
            relevant_email_chunks = self._get_relevant_email_chunks(query)
            query_and_texts = { 'query': query, 'texts': relevant_email_chunks }
            print(json.dumps(query_and_texts))