import openai
from fastapi import FastAPI
import pinecone
import json
import uvicorn
from pyngrok import ngrok
from fastapi.middleware.cors import CORSMiddleware
import nest_asyncio

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/request/{person_query}")
async def read_item(person_query: str):
    # get API key from top-right dropdown on OpenAI website
    openai.api_key = "INSERT KEY"

    # initialize connection to pinecone (get API key at app.pinecone.io)
    pinecone.init(
        api_key="INSERT KEY",
        environment="us-east4-gcp"  # find next to API key in console
    )

    pinecone.whoami()

    index_name = 'website-research-g-qa'

    # connect to index
    index = pinecone.Index(index_name)
    # view index stats
    index.describe_index_stats()

    embed_model = "text-embedding-ada-002"

    query = person_query

    res = openai.Embedding.create(
        input=[query],
        engine=embed_model
    )

    xq = res['data'][0]['embedding']

    res = index.query(xq, top_k=3, include_metadata=True)
    # print(res)

    limit = 1350

    # contexts = [x['metadata']['Specifications'] for x in res['matches']]

    contexts = []
    for match in res['matches']:
        context = {
            'name': match['metadata']['name'],
            'specifications': match['metadata']['Specifications'],
            'where': match['metadata']['collection']
        }
        contexts.append(context)

    # build our prompt with the retrieved contexts included
    prompt_start = (
        "Answer the question based on the context below in a friendly, elaborate way.\n\n"+
        "Context:\n"
    )
    prompt_end = (
        f"\n\nQuestion: {query}\nAnswer:"
    )
    # # append contexts until hitting limit
    # for i in range(1, len(contexts)):
    #     if len("\n\n---\n\n".join(contexts[:i])) >= limit:
    #         prompt = (
    #             prompt_start +
    #             "\n\n---\n\n".join(contexts[:i-1]) +
    #             prompt_end
    #         )
    #         break
    #     elif i == len(contexts)-1:
    #         prompt = (
    #             prompt_start +
    #             "\n\n---\n\n".join(contexts) +
    #             prompt_end
    #         )

    # append contexts until hitting limit
    for i in range(1, len(contexts)):
        if len("\n\n---\n\n".join(json.dumps(c) for c in contexts[:i])) >= limit:
            prompt = (
                prompt_start +
                "\n\n---\n\n".join(json.dumps(c) for c in contexts[:i-1]) +
                prompt_end
            )
            break
        elif i == len(contexts)-1:
            prompt = (
                prompt_start +
                "\n\n---\n\n".join(json.dumps(c) for c in contexts) +
                prompt_end
            )


    # now query text-davinci-003
    res = openai.Completion.create(
        engine='text-davinci-003',
        prompt=prompt,
        temperature=0,
        max_tokens=400,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        stop=None
    )
    # print(prompt)
    return {"Response": res['choices'][0]['text'].strip()}

ngrok_tunnel = ngrok.connect(8000)
print('Public URL:', ngrok_tunnel.public_url)
nest_asyncio.apply()
uvicorn.run(app, port=8000)
