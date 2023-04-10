# Main bip-email script
# subcommands: retrieve, query, gen-test-data
import argparse
import json
import logging
import requests

from datetime import datetime

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


def parse_arguments():
    parser = argparse.ArgumentParser(description='Bip Email')
    # add verbose argument
    parser.add_argument(
        '-v',
        '--verbose',
        action='store_true',
        help='Print debug messages')

    # Create subparsers
    subparsers = parser.add_subparsers(dest='subcommand', help='Subcommands')

    # Create parser for the "retrieve" subcommand
    parser_retrieve = subparsers.add_parser(
        'retrieve',
        help='Retrieve emails from Gmail and store them in Pinecone')
    # Add arguments to the "retrieve" subcommand: start_date, end_date
    # These arguments are required and should be parsed as dates in the format
    # YYYY-MM-DD
    parser_retrieve.add_argument(
        'start_date',
        help='Start date of the emails to retrieve (format: YYYY-MM-DD)',
        type=lambda s: datetime.strptime(s, '%Y-%m-%d').date())
    parser_retrieve.add_argument(
        'end_date',
        help='End date of the emails to retrieve (format: YYYY-MM-DD)',
        type=lambda s: datetime.strptime(s, '%Y-%m-%d').date())

    # Add optional argument to the "retrieve" subcommand: --clear-vs
    # Default value is False
    parser_retrieve.add_argument(
        '--clear-vs',
        action='store_true',
        help='Clear the vector store before adding the new emails')

    # Create parser for the "query" subcommand
    parser_query = subparsers.add_parser(
        'query',
        help='Ask a question to your emails and get the answer')
    # Add argument to the "query" subcommand: question
    parser_query.add_argument(
        'question',
        help='Question to ask to your emails')

    # Create parser for the "batch-query" subcommand
    parser_batch_query = subparsers.add_parser(
        'batch-query',
        help='Ask a list of questions to your emails and get the answers')
    # Add argument to the "batch-query" subcommand: question-list
    parser_batch_query.add_argument(
        'question_list',
        help='Path to the file containing the list of questions to ask, '
             'in JSONL format {"question": "question text"}')

    # Create parser for the "gen-test-data" subcommand
    parser_gen_test_data = subparsers.add_parser(
        'gen-test-data',
        help='Generate test data for the dust app in form of a jsonl file')
    # Add argument to the "gen-test-data" subcommand: query-list
    parser_gen_test_data.add_argument(
        'query_list',
        help='Path to the file containing the list of queries to ask')
    return parser.parse_args()


class BipCLI(object):

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

    @staticmethod
    def _call_dust_api(dust_input):
        dust_key = get_secret_key("dust")
        url = 'https://dust.tt/api/v1/apps/philipperolet/a2cf4c7458/runs'
        headers = {'Content-Type': 'application/json',
                   'Authorization': f'Bearer {dust_key}'}
        # create new dict from DUST_BODY and dust_input
        body = {**DUST_BODY, 'inputs': [dust_input]}
        response = requests.post(url, data=json.dumps(body), headers=headers)
        # return the parsed json
        return response.json()

    @staticmethod
    def _compute_answer(question, relevant_email_chunks):
        dust_input = {
            'texts': relevant_email_chunks,
            'query': question}
        result = BipCLI._call_dust_api(dust_input)
        return result['run']['results'][0][0]['value']['completion']['text']

    def _ask_emails(self, question):
        relevant_email_chunks = self._get_relevant_email_chunks(question)
        return self._compute_answer(question, relevant_email_chunks)

    def query_emails(self, question):
        print(self._ask_emails(question))

    def batch_query_emails(self, question_list):
        with open(question_list, 'r') as f:
            questions = [json.loads(line)['question'] for line in f]
        for question in questions:
            print(self._ask_emails(question) + '\n---\n')

    def gen_test_data(self, query_list):
        with open(query_list, 'r') as f:
            queries = [json.loads(line)['question'] for line in f]
        for query in queries:
            relevant_email_chunks = self._get_relevant_email_chunks(query)
            query_and_texts = { 'query': query, 'texts': relevant_email_chunks }
            print(json.dumps(query_and_texts))


if __name__ == '__main__':
    args = parse_arguments()
    bipCli = BipCLI()
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)
    if args.subcommand == 'retrieve':
        bipCli.retrieve_emails(args.start_date, args.end_date, args.clear_vs)
    elif args.subcommand == 'query':
        bipCli.query_emails(args.question)
    elif args.subcommand == 'batch-query':
        bipCli.batch_query_emails(args.question_list)
    elif args.subcommand == 'gen-test-data':
        bipCli.gen_test_data(args.query_list)
