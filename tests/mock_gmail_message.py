import base64

data = """
In the beginning there was the word, and the word was with God, and the word
was God. He was with God in the beginning. Through him all things were made;
without him nothing was made that has been made. In him was life, and that life
was the light of all mankind. The light shines in the darkness, and the
darkness has not overcome it.

The true light that gives light to everyone was coming into the world. He was
in the world, and though the world was made through him, the world did not
recognize him. He came to that which was his own, but his own did not receive
him. Yet to all who did receive him, to those who believed in his name, he gave
the right to become children of God—children born not of natural descent, nor
of human decision or a husband's will, but born of God. The Word became flesh
and made his dwelling among us. We have seen his glory, the glory of the one
and only Son, who came from the Father, full of grace and truth.

John testified concerning him. He cried out, saying, 'This is the one I spoke
about when I said, 'He who comes after me has surpassed me because he was
before me.' ' From the fullness of his grace we have all received one blessing
after another. For the law was given through Moses; grace and truth came
through Jesus Christ. No one has ever seen God, but God the One and Only, who
is at the Father's side, has made him known.

The Gospel of John, chapter 1, verses 1-18

Now, the first paragraph of the second chapter of the Gospel of John is a bit
longer, so I'll just give you the first sentence: "The next day John saw Jesus
coming toward him and said, 'Look, the Lamb of God, who takes away the sin of
the world!'"

The Gospel of John, chapter 2, verse 1

Coming back to the Genesis, the first chapter, the first verse: "In the
beginning God created the heavens and the earth.". Then, the second verse: "Now
the earth was formless and empty, darkness was over the surface of the deep,
and the Spirit of God was hovering over the waters."
"""
mock_gmail_message = {
    "id": "123",
    "threadId": "456",
    "internalDate": "789",
    "payload": {
        "headers": [
            {
                "name": "Subject",
                "value": "Test subject"
            },
            {   "name": "From",
                "value": "Test sender"
            },
            {
                "name": "To",
                "value": "Test recipient"
            },
            {
                "name": "Date",
                "value": "Test date"
            }
        ],
        "mimeType": "text/plain",
        "body": {
            "data": base64.urlsafe_b64encode(data.encode('utf-8'))
        }
    }
}
