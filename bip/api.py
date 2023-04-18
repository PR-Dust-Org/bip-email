import re
import urllib3
import json

from bip.utils import get_secret
from bip.config import logger
from bip.email.retriever import Retriever

ASK_EMAIL_DUST_PARAMS = {
    "url": 'https://dust.tt/api/v1/apps/philipperolet/a2cf4c7458/runs',
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

TEST_QUESTION_DUST_PARAMS = {
    "url": "https://dust.tt/api/v1/apps/philipperolet/16c337e35c/runs",
    "specification_hash":
    "655830201b20078ba07bf7f6a0bf0565141b8b4ed62af95e03f78fd2d3ac1629",
    "config": {
        "MODEL":
        {"provider_id": "openai",
         "model_id": "gpt-3.5-turbo",
         "use_cache": True}},
    "blocking": True
}


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
        logger.info('Done!')

    @classmethod
    def _call_dust_api(cls, dust_params, dust_inputs):
        # create the request headers and payload
        dust_key = get_secret("dust")
        # pop url from dust_params
        url = dust_params.pop('url')
        headers = {'Content-Type': 'application/json',
                   'Authorization': f'Bearer {dust_key}'}
        body = {**dust_params, 'inputs': dust_inputs}

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
        results = BipAPI._call_dust_api(
            ASK_EMAIL_DUST_PARAMS,
            dust_inputs)['run']['results']
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

    def test_questions(self, questions_file):
        print('Testing questions...')
        with open(questions_file, 'r') as f:
            questions = [json.loads(line) for line in f]

        # questions with an 'expected' field
        tested_questions = [question for question in questions
                            if 'expected' in question]
        # test all questions with an 'expected' field
        answers = self.batch_ask_emails(
            [q['question'] for q in tested_questions])
        dust_inputs = [{**question, 'answer': answer}
                       for question, answer in zip(tested_questions, answers)]
        dust_response = BipAPI._call_dust_api(
            TEST_QUESTION_DUST_PARAMS,
            dust_inputs)['run']['results']
        test_results = [r[0]['value']['completion']['text']
                        for r in dust_response]
        # count those where result contains 'PASS'
        pass_count = sum(1 for result in test_results if 'PASS' in result)

        # Print the results
        print(f'Tested questions: {len(tested_questions)} '
              f'out of {len(questions)}')
        print(f'Pass: {pass_count}')
        print(f'Fail: {len(tested_questions) - pass_count}\n---\n\n')

        test_data = zip(tested_questions, answers, test_results)

        # Sort test data with failed tests first
        test_data = sorted(test_data,
                           key=lambda x: 'PASS' not in x[2],
                           reverse=True)
        # Print the detailed results
        for question, answer, test_result in test_data:
            print(test_result)
            print(f'Question: {question["question"]}')
            print(f'Expected: {question["expected"]}')
            print(f'Actual: {answer}')
            print('---')
