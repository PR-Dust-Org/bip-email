# Test chunker
import random
import re
import unittest

from bip.email import chunker

from mock_gmail_message import mock_gmail_message, data


class TestChunker(unittest.TestCase):

    def test_chunker(self):
        enriched_chunks, metadatas = chunker.cut_message(mock_gmail_message, 100)
        self.maxDiff = None
        # shuffle the list of chunks in random order
        new_order = list(range(len(enriched_chunks)))
        random.shuffle(new_order)
        enriched_chunks = [enriched_chunks[i] for i in new_order]
        metadatas = [metadatas[i] for i in new_order]
        glued_back = chunker.glue_chunks(enriched_chunks, metadatas,
                                         keep_headfooter=False,
                                         delimiter="---")
        # using a regular expression, match identical text right before and
        # after the delimiter and replace it with a single occurence of the
        # text without the delimiter
        glued_back = re.sub(r"(.+)---\1", r"\1", glued_back)
        self.assertEqual(glued_back, re.sub(r"(.+)---\1", r"\1", glued_back))
        self.assertEqual(glued_back, data)
