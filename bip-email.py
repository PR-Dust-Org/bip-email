# Main bip-email script
# subcommands: retrieve, query, gen-test-data
import argparse
import logging
from datetime import datetime

from bip.email.retriever import Retriever, get_secret_key

DUST_BODY = {"specification_hash": "0b22d94003fabffa4784106518abeb905cf5936f2c4d08cf76c8ba81c622e703",
             "config": {"INTENT_QUESTION":{"provider_id":"openai",
                                           "model_id":"gpt-3.5-turbo",
                                           "use_cache":True},
                        "MODEL_1": {"provider_id":"openai",
                                   "model_id":"gpt-3.5-turbo",
                                   "use_cache":True},
                        "MODEL": {"provider_id":"openai","model_id":"gpt-4",
                                  "use_cache": True}},
                   "blocking": True}


def parse_arguments():
    parser = argparse.ArgumentParser(description='Bip Email')

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

    # Create parser for the "gen-test-data" subcommand
    parser_gen_test_data = subparsers.add_parser(
        'gen-test-data',
        help='Generate test data for the dust app in form of a jsonl file')
    # Add argument to the "gen-test-data" subcommand: query-list
    parser_gen_test_data.add_argument(
        'query_list',
        help='Path to the file containing the list of queries to ask')
    return parser.parse_args()


def _get_relevant_email_chunks(retriever, question):
    result = (retriever
              .query(question, top_k=5, include_metadata=True)
              .get('matches'))
    return [result['metadata']['text'] for result in result]


def retrieve_emails(start_date, end_date, clear_vs):
    retriever = Retriever()
    if clear_vs:
        retriever.delete_all_emails()
    retriever.update_email_index(start_date, end_date)
    logging.info('Done!')


def _call_dust_api(dust_input):
    import requests
    import json
    dust_key = get_secret_key("dust")
    url = 'https://dust.tt/api/v1/apps/philipperolet/a2cf4c7458/runs'
    headers = {'Content-Type': 'application/json',
               'Authorization': f'Bearer {dust_key}'}
    # create new dict from DUST_BODY and dust_input
    body = {**DUST_BODY, 'inputs': [dust_input]}
    response = requests.post(url, data=json.dumps(body), headers=headers)
    # return the parsed json
    return response.json()


def _compute_answer(question, relevant_email_chunks):
    dust_input = {
        'texts': relevant_email_chunks,
        'query': question}
    result = _call_dust_api(dust_input)
    return result['run']['results'][0][0]['value']['completion']['text']


def query_emails(question):
    retriever = Retriever()
    relevant_email_chunks = _get_relevant_email_chunks(retriever, question)
    print(_compute_answer(question, relevant_email_chunks))


if __name__ == '__main__':
    args = parse_arguments()
    if args.subcommand == 'retrieve':
        retrieve_emails(args.start_date, args.end_date, args.clear_vs)
    elif args.subcommand == 'query':
        query_emails(args.question)
    elif args.subcommand == 'gen-test-data':
        print('Not implemented yet!')
