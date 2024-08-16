# GoogleDriveRAG
A RAG(retrieval augmented generation) that utilizes the google drive API and openAI API to answer user prompts based on the documents within their google drive.

A number of libraries and APIs were used including pandas, numpy, the openAI API, and the google API. The program includes a basic UI to interact with the RAG, prompting the user for input and giving directions on usage. The google drive API is used to download the users google docs which are then stored in a csv file. The RAG works by first loading the documents into a pandas dataframe, and then using openAIs embedding model to create vector embeddings of the docs contents. These embeddings are then compared to the vector embedding of the query to retrieve relevant documents which are provided as context to the openAI API which then answers the question.

The code is fully functional, however the openAI API key has been redacted within the backend.py file, and the client_secret has been redacted in the client_secret.json file. Both an API key and client_secret must be provided to run the code. 
