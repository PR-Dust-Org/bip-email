# Test chunker
import unittest

from bip import chunker

from mock_gmail_message import mock_gmail_message


class TestChunker(unittest.TestCase):

    def test_chunker(self):
        enriched_chunks, _ = chunker.cut_message(mock_gmail_message)
        shuffled_chunks = chunker.shuffle_chunks(enriched_chunks)
        print(enriched_chunks)
        glued_back = chunker.glue_chunks(shuffled_chunks, keep_header=False)
        self.assertEqual(glued_back,
                         mock_gmail_message['payload']['body']['data'])
