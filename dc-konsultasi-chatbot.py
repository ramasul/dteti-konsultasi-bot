import discord
import os
import signal
import sys

from groq import Groq
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

class Konsultasi(discord.Client):
    def __init__(self, intents):
        super().__init__(intents = intents)
        self.konsultasi = False
        self.quits = ["bye"]

    async def on_ready(self):
        """Triggered when connecting to Discord."""
        print(f'Connected as {self.user}.')

    async def on_message(self, message: discord.Message):
        """Triggered when receiving a message."""
        # Ignore messages sent by the bot itself
        if message.author == self.user:
            return
            
        if(message.content == '!konsultasi'):
            self.konsultasi = True
            query = "Perkenalkan diri anda dengan singkat"
            context = get_relevant_context_from_db(query)
            prompt = generate_rag_prompt(query=query, context=context)
            answer = generate_answer(prompt=prompt)
            await message.channel.send(answer)
            return

        print(f'Received a message from {message.author}: {message.content}')

        if(self.konsultasi): 
            """Triggered when receiving a message."""
            
            print(f'Received a message from {message.author}: {message.content}')
            query = message.content
            if query.lower() in self.quits:
                await message.channel.send(generate_answer(query + ". Thank you for talking with me"))
                self.konsultasi = False
                return
            context = get_relevant_context_from_db(query)
            prompt = generate_rag_prompt(query=query, context=context)
            answer = generate_answer(prompt=prompt)
            await message.channel.send(answer)

def generate_rag_prompt(query, context):
    escaped = context.replace("'","").replace('"', "").replace("\n"," ")
    prompt = ("""
    You are a helpful, informative, and friendly bot to be a place for [STUDENT] to consult. \
    [STUDENT] is an undergraduate student from Departement of Electrical Engineering and Information Technology (DTETI) from Universitas Gadjah Mada. \
    You will answer using text from the reference context included below. \
    Please answer using the same language as what [STUDENT] say. \
    Be sure to respond in a complete sentence, being comprehensive, including all relevant background information. \
    If the context is relevant to the answer, you could add anything that you know. \
    Please keep a friendly and conversational tone. \
    If the context is irrelevant to the answer, you may ignore it, unless if it's related to [STUDENT] consulting to you.
                [STUDENT]: '{query}'
                CONTEXT: '{context}'
              
              ANSWER:
              """).format(query=query, context=context)
    return prompt

def get_relevant_context_from_db(query):
    context = ""
    embedding_function=HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vector_db = Chroma(persist_directory="./chroma_db_nccn", embedding_function=embedding_function)
    search_results = vector_db.similarity_search(query, k=6)
    for result in search_results:
        context += result.page_content + "\n"
    return context

def generate_answer(prompt):
    messages = [
        {"role": "system", "content": prompt }
    ]
    # generate response
    chat_response = groq_client.chat.completions.create(
        model="llama3-70b-8192",
        messages=messages
    )
    return chat_response.choices[0].message.content


with open('.discord_token') as f:
    token = f.read().strip()

with open('.groq_key') as f:
    GROQ_API_KEY = f.read().strip()
groq_client = Groq(api_key=GROQ_API_KEY)

intents = discord.Intents.default()
intents.message_content = True
client = Konsultasi(intents=intents)
client.run(token)
