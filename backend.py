import pandas as pd
from openai import OpenAI
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import numpy as np
import time
import random

SCOPES = ['https://www.googleapis.com/auth/drive.readonly', 'https://www.googleapis.com/auth/documents.readonly']
client = OpenAI(api_key='***REDACTED***') # An openAI API key must be provided for the code to function.


def authenticate():
    flow = InstalledAppFlow.from_client_secrets_file('client_secret.json', SCOPES)  # A client_secret must be provided within the client_secret.json file before the code will run.
    creds = flow.run_local_server(port=8080)
    return creds

def list_google_docs(drive_service):
    query = "mimeType='application/vnd.google-apps.document'"
    page_token = None
    docs = []

    while True:
        results = drive_service.files().list(
            q=query,
            pageSize=100,
            fields="nextPageToken, files(id, name)",
            pageToken=page_token
        ).execute()
        items = results.get('files', [])
        docs.extend(items)
        page_token = results.get('nextPageToken', None)
        if not page_token:
            break

    return docs

def get_doc_content(docs_service, doc_id):
    doc = docs_service.documents().get(documentId=doc_id).execute()
    content = doc.get('body').get('content', [])
    text = ''

    for element in content:
        if 'paragraph' in element:
            for text_run in element.get('paragraph').get('elements', []):
                if 'textRun' in text_run:
                    text += text_run.get('textRun').get('content', '')

    return text


def make_embedding(text, model="text-embedding-3-large"):
    text = text.replace("\n", " ")
    embed = client.embeddings.create(input = [text], model = model).data[0].embedding
    print("EMBEDDED")
    return embed

def split_string(input_string, chunk_size):
    return [input_string[i:i + chunk_size] for i in range(0, len(input_string), chunk_size)]


def docs_to_df():
    # Authenticate the user
    creds = authenticate()
    print("AUTHENTICATED!")
    # Build the Drive and Docs API services
    drive_service = build('drive', 'v3', credentials=creds)
    docs_service = build('docs', 'v1', credentials=creds)

    # List all Google Docs
    docs = list_google_docs(drive_service)

    # Initialize a DataFrame
    df = pd.DataFrame(columns=['Document Name', 'Document ID', 'Content'])

    # Retrieve and store content of each Google Doc
    num=0
    for doc in docs:
        print(f"Downloaded doc {num}")
        num+=1
        doc_id = doc['id']
        doc_name = doc['name']
        content = ''
        print(f"Attempting to download {doc_name}")
        try:
            content = get_doc_content(docs_service, doc_id)
        except TimeoutError:
            print('trying one more time after waiting a few seconds')
            time.sleep(7+random.randint(3,6))
            print('trying again now')
            try:
                content = get_doc_content(docs_service, doc_id)
            except TimeoutError:
                print('failed again, document is likely too big and moving on')
        if len(content)<10000:
            try:
                embedding = make_embedding(content)
                new_row = pd.DataFrame({'Document Name': [doc_name], 'Document ID': [doc_id], 'Content': [content], 'Embedding': [embedding]})
                df = pd.concat([df, new_row], ignore_index = True)
            except Exception as e:
                print("There was an error embedding and this document will be ignored")
        else:
            chunks = split_string(content, 10000)
            for chunk in chunks:
                try:
                    embedding = make_embedding(chunk)
                    new_row = pd.DataFrame(
                        {'Document Name': [doc_name], 'Document ID': [doc_id], 'Content': [chunk],
                         'Embedding': [embedding]})
                    df = pd.concat([df, new_row], ignore_index = True)
                except Exception as e:
                    print(f"There was an error embedding of type {e} and this document will be ignored. The text that caused this error is '{chunk}'")
    # Save the DataFrame to a CSV file
    name = input("What would you like to name this csv \n")
    df.to_csv(name + ".csv", index=False)
    return df

def load_df():
    name = input("What is the name of the csv? ")
    def custom_converter(value):
        return np.array(eval(value))
    try:
        df = pd.read_csv(name, converters = {'Embedding':custom_converter})
    except FileNotFoundError as e:
        print("No file was found with this name, please try again")
        df = load_df()
    return df

def RAGquery(df, question):
    question_embedding = make_embedding(question)
    def dot_distance(page_embedding):
        try:
            return np.dot(page_embedding, question_embedding)
        except TypeError:
            print("there was a type error so this document will be discarded")
            return 0
    df['distance'] = df['Embedding'].apply(dot_distance)
    df.sort_values('distance', ascending=False, inplace=True)
    context = 'DOCUMENT NAME: ' + df['Document Name'].iloc[0]+":\n{"+df['Content'].iloc[0]+"}\n"+'DOCUMENT NAME: '+df['Document Name'].iloc[1]+":\n{"+df['Content'].iloc[1]+"}\n"+'DOCUMENT NAME: '+df['Document Name'].iloc[2]+":\n{"+df['Content'].iloc[2]+"}\n"
    response = client.chat.completions.create(
        model = "gpt-3.5-turbo",
        messages = [
            {"role": "system", "content": "You are an assistant that answers questions based primarily on given documents "},
            {"role": "user", "content": question},
            {"role": "assistant", "content": f"Answer the question based on the following documents, making sure to name the title of the document that relevant information comes from. \n {context}"}
        ]
    )
    return response
