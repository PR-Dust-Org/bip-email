import copy
import re
import urllib3
import json
from bip.email import chunker

from bip.utils import get_secret
from bip.config import logger
from bip.email.retriever import Retriever

ASK_EMAIL_DUST_PARAMS = {
    "url": 'https://dust.tt/api/v1/apps/philipperolet/a2cf4c7458/runs',
    "specification_hash":
    "0434c19c6eb5bbc7cf4d8f666382148113a92df60366146c778bd4b8da966903",
    "config": {
        "FINAL_ANALYSIS": {"provider_id": "openai",
                           "model_id": "text-davinci-003",
                           "use_cache": True},
        "MODEL": {"provider_id": "openai",
                  "model_id": "text-davinci-003",
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

    def __init__(self, user_email, retriever_namespace):
        self._retriever = Retriever(user_email, retriever_namespace)

    def _get_texts_from_matching_data(self, vector_metadata,
                                      max_texts=4,
                                      texts_acc=[]):

        if (len(texts_acc) >= max_texts or not vector_metadata):
            return texts_acc

        # get the first chunk and add all chunks with the same message id
        message_chunks_id = vector_metadata[0]['metadata']['message_id']

        def chunks_with_same_message_id(chunk):
            return (chunk['metadata']['message_id'] == message_chunks_id)
        message_chunks = list(filter(chunks_with_same_message_id,
                                     vector_metadata))

        # remove the chunks from the list
        for chunk in message_chunks:
            vector_metadata.remove(chunk)

        # Glue the chunks
        enriched_chunks = [chunk['metadata']['text']
                           for chunk in message_chunks]
        metadatas = [chunk['metadata'] for chunk in message_chunks]
        message_text = chunker.glue_chunks(enriched_chunks, metadatas)

        return self._get_texts_from_matching_data(vector_metadata,
                                                  max_texts,
                                                  texts_acc + [message_text])

    def _get_relevant_texts(self, question):
        matching_vectors = (self._retriever
                            .query(question, top_k=32, include_metadata=True)
                            .get('matches'))
        return self._get_texts_from_matching_data(matching_vectors)

    def retrieve_emails(self, start_date, end_date, clear_vs):
        if clear_vs:
            self._retriever.delete_all_emails()
        self._retriever.update_email_index(start_date, end_date)
        logger.info('Done!')

    @classmethod
    def _call_dust_api(cls, dust_params, dust_inputs):
        dust_params = copy.deepcopy(dust_params)
        logger.info('Calling Dust endpoint')
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
        logger.info('Results received from Dust')
        return json.loads(response.data.decode('utf-8'))

    def _create_dust_inputs(self, questions):
        relevant_email_chunks = [self._get_relevant_texts(question)
                                 for question in questions]
        return [{'texts': chunks, 'question': question}
                for question, chunks in zip(questions, relevant_email_chunks)]

    def _parse_dust_results(self, results):
        def _parse_result(result):
            return re.split(r'Réponse\W*:\W?',
                            result[0]['value']['completion']['text'])[1]
        return [result[0]['value']['answer'] for result in results]

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
            questions = [json.loads(line)['question'] for line in f
                         if 'expected' in json.loads(line)]
        print("\n".join([json.dumps(x)
                         for x in self._create_dust_inputs(questions)]))

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
