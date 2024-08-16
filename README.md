# GoogleDriveRAG
A RAG(retrieval augmented generation) that utilizes the google drive API and openAI API to answer user prompts based on the documents within their google drive.

A number of libraries and APIs were used including pandas, numpy, the openAI API, and the google API. The program includes a basic UI to interact with the RAG, prompting the user for input and directions. The google drive API is used to download the users google docs which are then stored in a csv file. The RAG works by loading the doc into a python dataframe, and then using openAIs embedding model to create vector embeddings of the docs contents, which are then compared to the vector embedding of the query to retrieve relevant documents and then answer the question again using the openAI API.

The code is fully functional, however the openAI API key has been redacted within the backend.py file, and the client_secret has been redacted in the client_secret.json file. Both an API key and client_secret must be provided to run the code. 
