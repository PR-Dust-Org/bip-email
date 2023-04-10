import os
import openai

# Create an embedding for the question "What is the meaning of life?"
openai.api_key = os.getenv("OPENAI_API_KEY")
question = "What is the meaning of life?"
question_embedding = openai.Embedding.create(
    input=question,
    model="text-embedding-ada-002")
print(question_embedding['data'][0]['embedding'][:10])
