import re
import urllib3
import json
import logging
from bip.utils import get_secret

from bip.email.retriever import Retriever

DUST_BODY = {
    "specification_hash":
    "250113fe7361a08f0108f2c2a27366e3e755fd80fc732838b2f9262ba0f0e355",
    "config": {
        "INTENT_QUESTION":
        {"provider_id": "openai",
         "model_id": "gpt-3.5-turbo",
         "use_cache": True},
        "MODEL_1":
        {"provider_id": "openai",
         "model_id": "gpt-3.5-turbo",
         "use_cache": True},
        "MODEL":
        {"provider_id": "openai",
         "model_id": "gpt-3.5-turbo",
         "use_cache": True}},
    "blocking": True}


class BipAPI(object):

    _http = urllib3.PoolManager()

    def __init__(self, user_email):
        self._retriever = Retriever(user_email)

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
    def _call_dust_api(cls, dust_inputs):
        # create the request headers and payload
        dust_key = get_secret("dust")
        url = 'https://dust.tt/api/v1/apps/philipperolet/a2cf4c7458/runs'
        headers = {'Content-Type': 'application/json',
                   'Authorization': f'Bearer {dust_key}'}
        body = {**DUST_BODY, 'inputs': dust_inputs}

        # make the request
        response = cls._http.request(
            'POST',
            url,
            body=json.dumps(body).encode('utf-8'),
            headers=headers)
        return json.loads(response.data.decode('utf-8'))

    def _create_dust_inputs(self, questions):
        relevant_email_chunks = [self._get_relevant_email_chunks(question)
                                 for question in questions]
        return [{'texts': chunks, 'question': question}
                for question, chunks in zip(questions, relevant_email_chunks)]

    def _parse_dust_results(self, results):
        def _parse_result(result):
            return re.split(r'Réponse\W*:\W?',
                            result[0]['value']['completion']['text'])[1]
        return [_parse_result(result) for result in results]

    def batch_ask_emails(self, questions):
        dust_inputs = self._create_dust_inputs(questions)
        results = BipAPI._call_dust_api(dust_inputs)['run']['results']
        return self._parse_dust_results(results)

    def batch_ask_emails_from_file(self, questions_file):
        with open(questions_file, 'r') as f:
            questions = [json.loads(line)['question'] for line in f]
        return self.batch_ask_emails(questions)

    def ask_emails(self, question):
        return self.batch_ask_emails([question])[0]

    def gen_test_data(self, questions_file):
        with open(questions_file, 'r') as f:
            questions = [json.loads(line)['question'] for line in f]
        print(json.dumps(self._create_dust_inputs(questions)))

    def test_asks(self, questions_file):
        # with open(questions_file, 'r') as f:
        #    questions = [json.loads(line)['question'] for line in f]
        raise NotImplementedError
