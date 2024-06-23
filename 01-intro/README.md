
# Task

## Homework: Introduction

In this homework, we'll learn more about search and use Elastic Search for practice.

### Set Up Environment

Go to the working directory

```bash
cd llm_zoomcamp/llm-zoomcamp-2024/
```

Install the required packages with `pipenv` (install it first `pip install pipenv`)

```bash
pipenv install jupyter tqdm pandas scikit-learn openai elasticsearch --python 3.11
```

It will create `Pipfile` and `Pipfile.lock` in your working directory

## Q1. Running Elastic

Run Elastic Search 8.4.3, and get the cluster information. If you run it on localhost, this is how you do it:

```bash
curl localhost:9200
```

What's the `version.build_hash` value?

`42f05b9372a9a4a470db3b52817899b99a76ee73` 

### How to run Elasticsearch?

create `docker-compose.yml` 

```yaml
services:
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.4.3
    container_name: elasticsearch-zoomcamp
    environment:
      - discovery.type=single-node
      - xpack.security.enabled=false
    ports:
      - "9200:9200"
      - "9300:9300"
    volumes:
      - ./esdata:/usr/share/elasticsearch/data

  kibana:
    image: docker.elastic.co/kibana/kibana:8.4.3
    container_name: kibana-zoomcamp
    environment:
      - ELASTICSEARCH_HOSTS=http://elasticsearch:9200
    ports:
      - "5601:5601"
    depends_on:
      - elasticsearch
```

In the **`docker-compose.yml`** file above, I’ve added an optional service, **Kibana**, to visualize the data stored in Elasticsearch.

```bash
docker compose up --build
```

<aside>
<img src="/icons/warning_yellow.svg" alt="/icons/warning_yellow.svg" width="40px" /> If you encounter an error or an unexpected exit when starting Docker Compose with Elasticsearch data volume mapping,

```yaml
services:
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.4.3
    container_name: elasticsearch-zoomcamp
    environment:
      - discovery.type=single-node
      - xpack.security.enabled=false
    ports:
      - "9200:9200"
      - "9300:9300"
    volumes:
      **- ./esdata:/usr/share/elasticsearch/data**
      
```

the error,

```
"@timestamp":"2024-06-21T08:35:31.532Z", "log.level":"ERROR", "message":"fatal exception while booting Elasticsearch", "ecs.version": "1.2.0","service.name":"ES_ECS","event.dataset":"elasticsearch.server","process.thread.name":"main","log.logger":"org.elasticsearch.bootstrap.Elasticsearch","elasticsearch.node.name":"d3225b52c64d","elasticsearch.cluster.name":"docker-cluster","error.type":"java.lang.IllegalStateException","error.message":"failed to obtain node locks, tried [/usr/share/elasticsearch/data]; maybe these locations are not writable or multiple nodes were started on the same data path?","error.stack_trace":"java.lang.IllegalStateException: failed to obtain node locks, tried [/usr/share/elasticsearch/data]; maybe these locations are not writable or multiple nodes were started on the same data path?\n\tat org.elasticsearch.server@8.4.3/org.elasticsearch.env.NodeEnvironment.<init>(NodeEnvironment.java:285)\n\tat org.elasticsearch.server@8.4.3/org.elasticsearch.node.Node.<init>(Node.java:456)\n\tat org.elasticsearch.server@8.4.3/org.elasticsearch.node.Node.<init>(Node.java:311)\n\tat org.elasticsearch.server@8.4.3/org.elasticsearch.bootstrap.Elasticsearch$2.<init>(Elasticsearch.java:214)\n\tat org.elasticsearch.server@8.4.3/org.elasticsearch.bootstrap.Elasticsearch.initPhase3(Elasticsearch.java:214)\n\tat org.elasticsearch.server@8.4.3/org.elasticsearch.bootstrap.Elasticsearch.main(Elasticsearch.java:67)\nCaused by: java.io.IOException: failed to obtain lock on /usr/share/elasticsearch/data\n\tat org.elasticsearch.server@8.4.3/org.elasticsearch.env.NodeEnvironment$NodeLock.<init>(NodeEnvironment.java:230)\n\tat org.elasticsearch.server@8.4.3/org.elasticsearch.env.NodeEnvironment$NodeLock.<init>(NodeEnvironment.java:198)\n\tat org.elasticsearch.server@8.4.3/org.elasticsearch.env.NodeEnvironment.<init>(NodeEnvironment.java:277)\n\t... 5 more\nCaused by: java.nio.file.NoSuchFileException: /usr/share/elasticsearch/data/node.lock\n\tat java.base/sun.nio.fs.UnixException.translateToIOException(UnixException.java:92)\n\tat java.base/sun.nio.fs.UnixException.rethrowAsIOException(UnixException.java:106)\n\tat java.base/sun.nio.fs.UnixException.rethrowAsIOException(UnixException.java:111)\n\tat java.base/sun.nio.fs.UnixPath.toRealPath(UnixPath.java:825)\n\tat org.apache.lucene.core@9.3.0/org.apache.lucene.store.NativeFSLockFactory.obtainFSLock(NativeFSLockFactory.java:94)\n\tat org.apache.lucene.core@9.3.0/org.apache.lucene.store.FSLockFactory.obtainLock(FSLockFactory.java:43)\n\tat org.apache.lucene.core@9.3.0/org.apache.lucene.store.BaseDirectory.obtainLock(BaseDirectory.java:44)\n\tat org.elasticsearch.server@8.4.3/org.elasticsearch.env.NodeEnvironment$NodeLock.<init>(NodeEnvironment.java:223)\n\t... 7 more\n\tSuppressed: java.nio.file.AccessDeniedException: /usr/share/elasticsearch/data/node.lock\n\t\tat java.base/sun.nio.fs.UnixException.translateToIOException(UnixException.java:90)\n\t\tat java.base/sun.nio.fs.UnixException.rethrowAsIOException(UnixException.java:106)\n\t\tat java.base/sun.nio.fs.UnixException.rethrowAsIOException(UnixException.java:111)\n\t\tat java.base/sun.nio.fs.UnixFileSystemProvider.newByteChannel(UnixFileSystemProvider.java:218)\n\t\tat java.base/java.nio.file.Files.newByteChannel(Files.java:380)\n\t\tat java.base/java.nio.file.Files.createFile(Files.java:658)\n\t\tat org.apache.lucene.core@9.3.0/org.apache.lucene.store.NativeFSLockFactory.obtainFSLock(NativeFSLockFactory.java:84)\n\t\t... 10 more\n"}
```

it can be solved by ensuring the directory exists and is writable

```bash
mkdir -p ./esdata
chmod 777 ./esdata
```

</aside>

## Getting the data

Now let's get the FAQ data. You can run this snippet:

```python
import requests

docs_url = '<https://github.com/DataTalksClub/llm-zoomcamp/blob/main/01-intro/documents.json?raw=1>'
docs_response = requests.get(docs_url)
documents_raw = docs_response.json()

documents = []

for course in documents_raw:
    course_name = course['course']

    for doc in course['documents']:
        doc['course'] = course_name
        documents.append(doc)

```

Note that you need to have the `requests` library:

```bash
pip install requests

```

## Q2. Indexing the data

Index the data in the same way as was shown in the course videos. Make the `course` field a keyword and the rest should be text.

Don't forget to install the ElasticSearch client for Python:

```bash
pip install elasticsearch

```

Which function do you use for adding your data to elastic?

- `insert`
- **`index`**
- `put`
- `add`

## Q3. Searching

Now let's search in our index.

We will execute a query "How do I execute a command in a running docker container?".

Use only `question` and `text` fields and give `question` a boost of 4, and use `"type": "best_fields"`.

What's the score for the top ranking result?

- 94.05
- **84.05**
- 74.05
- 64.05

Look at the `_score` field.

```python
user_question = "How do I execute a command in a running docker container?"

search_query = {
    "size": 5,
    "query": {
        "bool": {
            "must": {
                "multi_match": {
                    "query": user_question,
                    "fields": ["question^4", "text", "section"],
                    "type": "best_fields"
                }
            }
        }
    }
}

response = es.search(index=index_name, body=search_query)

print(response['hits']['hits'][0]['_score']) # first rank
```

## Q4. Filtering

Now let's only limit the questions to `machine-learning-zoomcamp`.

Return 3 results. What's the 3rd question returned by the search engine?

- How do I debug a docker container?
- **How do I copy files from a different folder into docker container’s working directory?**
- How do Lambda container images work?
- How can I annotate a graph?

### How is the body of the query?

Notes: we keep the setting from Q3, to boost `question` by 4.

```python
search_query = {
    "size": 3,
    "query": {
        "bool": {
            "must": {
                "multi_match": {
                    "query": user_question,
                    "fields": ["question^4", "text", "section"],
                    "type": "best_fields"
                }
            },
            "filter": {
                "term": {
                    "course": "machine-learning-zoomcamp"
                }
            }
        }
    }
}
```

Let’s encapsulate the search query into a function.

```python
from elasticsearch import Elasticsearch, ApiError

# Initialize Elasticsearch client
es = Elasticsearch("http://localhost:9200")

def retrieve_documents(user_question, index_name="course-questions"):
    # Define the search query
    search_query = {
        "size": 3,
        "query": {
            "bool": {
                "must": {
                    "multi_match": {
                        "query": user_question,
                        "fields": ["question^4", "text", "section"],
                        "type": "best_fields"
                    }
                },
                "filter": {
                    "term": {
                        "course": "machine-learning-zoomcamp"
                    }
                }
            }
        }
    }

    try:
        # Execute the search query
        response = es.search(
            index=index_name,
            body=search_query
        )
        return [hit for hit in response['hits']['hits']]
    except ApiError as e:
        print(f"Error executing search query: {e}")
        return []
    
```

```python
user_question = "How do I execute a command in a running docker container?"
results = retrieve_documents(user_question)
for result in results:
    question = result['_source']['question']
    print(f"Question: {question}", end="\n\n")
    
    
# Question: How do I debug a docker container?
#
# Question: How do I copy files from my local machine to docker container?
#
# Question: How do I copy files from a different folder into docker container’s working directory?
```

## Q5. Building a prompt

Now we're ready to build a prompt to send to an LLM.

Take the records returned from Elasticsearch in Q4 and use this template to build the context. Separate context entries by two linebreaks (`\\n\\n`)

```python
context_template = """
Q: {question}
A: {text}
""".strip()

```

Now use the context you just created along with the "How do I execute a command in a running docker container?" question
to construct a prompt using the template below:

```
prompt_template = """
You're a course teaching assistant. Answer the QUESTION based on the CONTEXT from the FAQ database.
Use only the facts from the CONTEXT when answering the QUESTION.

QUESTION: {question}

CONTEXT:
{context}
""".strip()

```

What's the length of the resulting prompt? (use the `len` function)

- 962
- **1462**
- 1962
- 2462

Let’s use string formatting to help answer the task

```python
context_entries = []
for result in results:
    question = result['_source']['question']
    text = result['_source']['text']
    **context = context_template.format(question=question, text=text)**
    context_entries.append(context)

contexts = '\n\n'.join(context_entries)
print(contexts)
```

```python
question = "How do I execute a command in a running docker container?"
prompt = prompt_template.format(question=question, context=contexts)
len(prompt)
```

## Q6. Tokens

When we use the OpenAI Platform, we're charged by the number of
tokens we send in our prompt and receive in the response.

The OpenAI python package uses `tiktoken` for tokenization:

```bash
pip install tiktoken

```

Let's calculate the number of tokens in our query:

```python
encoding = tiktoken.encoding_for_model("gpt-4o")

```

Use the `encode` function. How many tokens does our prompt have?

- 122
- 222
- **322**
- 422

```python
encoding = tiktoken.encoding_for_model("gpt-4o")
tokens = encoding.encode(prompt)
len(tokens)
```

Note: to decode back a token into a word, you can use the `decode_single_token_bytes` function:

```python
encoding.decode_single_token_bytes(63842)

```

## Bonus: generating the answer (ungraded)

Let's send the prompt to OpenAI. What's the response?

Note: you can replace OpenAI with Ollama. See module 2.

```python
from openai import OpenAI

client = OpenAI()

response = client.chat.completions.create(
    model='gpt-4o',
    messages=[
        {'role': 'user', 'content': prompt}
    ]
)

print(response.to_json())
```

```json
{
  "id": "chatcmpl-9dJTn50Kzl7RglfmOJDQu0S1zjTzo",
  "choices": [
    {
      "finish_reason": "stop",
      "index": 0,
      "logprobs": null,
      "message": {
        "content": "To execute a command in a running Docker container, you can use the `docker exec` command. First, find the container ID of the running container by using the `docker ps` command. Then, use `docker exec -it` followed by the container ID and the command you want to execute. For example, to start a bash session in the running container, you would use the following commands:\n\n1. Find the container ID:\n   ```bash\n   docker ps\n   ```\n\n2. Execute the bash command in the specific running container:\n   ```bash\n   docker exec -it <container-id> bash\n   ```",
        "role": "assistant"
      }
    }
  ],
  "created": 1719156699,
  "model": "gpt-4o-2024-05-13",
  "object": "chat.completion",
  "system_fingerprint": "fp_3e7d703517",
  "usage": {
    "completion_tokens": 128,
    "prompt_tokens": 329,
    "total_tokens": 457
  }
}

```

## Bonus: calculating the costs (ungraded)

Suppose that on average per request we send 150 tokens and receive back 250 tokens.

How much will it cost to run 1000 requests?

You can see the prices [here](https://openai.com/api/pricing/)

On June 17, the prices for gpt4o are:

- Input: $0.005 / 1K tokens
- Output: $0.015 / 1K tokens

You can redo the calculations with the values you got in Q6 and Q7.

```python
# for gpt-4o, in dolars per 1M tokens
input_cost = 5
output_cost = 15

def calculate_cost(input_tokens, output_tokens):
    total_cost = input_tokens * input_cost / 10e6 + output_tokens * output_cost / 10e6
    return total_cost

input_tokens = response.usage.prompt_tokens
output_tokens = response.usage.completion_tokens

cost_per_request = calculate_cost(input_tokens, output_tokens)

num_requests = 1000

total_cost = cost_per_request * num_requests
print(f"Total cost for {num_requests} requests: ${total_cost:.2f}")

# Total cost for 1000 requests: $0.36
```

## Submit the results

- Submit your results here: https://courses.datatalks.club/llm-zoomcamp-2024/homework/hw1
- It's possible that your answers won't match exactly. If it's the case, select the closest one.