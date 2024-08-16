import backend
def first_menu():
    option = input(
        "Please choose one of the following options:\n1) turn a drive into a csv\n2) load a previous csv\n")
    while option != '1' and option != '2':
        option = input("Please choose one of the following options:\n1) load a new drive\n2) load a previous csv\n")
    if option == '1':
        df = backend.docs_to_df()
    elif option == '2':
        df = backend.load_df()
    second_menu(df)

def second_menu(df):
    option = input("\nPlease choose one of the following options:\n1) Submit a question for the RAG\n2) return to the first menu\n3) quit\n")
    while option != '1' and option != '2' and option != '3':
        option = input(
            "Please choose one of the following options:\n1) Submit a question for the RAG\n2) return to the first menu\n3) quit\n")
    if option == '1':
        question = input("\nWhat would you like to ask?\n")
        print("\n"+backend.RAGquery(df, question).choices[0].message.content)
        second_menu(df)
    elif option =='2':
        first_menu()
    elif option =='3':
        return
