# Test chunker
import random
import unittest

from bip.email import chunker

from mock_gmail_message import mock_gmail_message, data


class TestChunker(unittest.TestCase):

    def test_chunker(self):
        enriched_chunks, _ = chunker.cut_message(mock_gmail_message, 500)
        # shuffle the list of chunks in random order
        random.shuffle(enriched_chunks)
        print(enriched_chunks)
        glued_back = chunker.glue_chunks(enriched_chunks,
                                         keep_header=False,
                                         delimiter="")
        self.assertEqual(glued_back, data)
