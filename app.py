import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langgraph.prebuilt import create_react_agent
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_community.utilities import SQLDatabase
from langgraph.checkpoint.memory import MemorySaver


# Modèle
api_key = ""
llm = ChatOpenAI(api_key=api_key)

# Base de données
db = SQLDatabase.from_uri("sqlite:///ecommerce.db")

# Donner à l'agent l'accès à la base de données
toolkit = SQLDatabaseToolkit(db=db, llm=llm)
tools = toolkit.get_tools()

prompt = """
Étant donné une question en entrée, créer d'abord une requête {dialect}
syntaxiquement correcte, l'exécuter et renvoyer la réponse à la question posée.

Utilise uniquement les tables suivantes :
{table_info}

Question : {question}
"""

# Agent
memory = MemorySaver()
agent_executor = create_react_agent(llm, tools, checkpointer=memory)


# Fonction pour générer une requête SQL et obtenir les résultats
def generate_sql_and_get_results(question: str):
    """
    Utilise le modèle LLM pour convertir une question en langage naturel en une
    requête SQL, l'exécute, et retourne la requête et la réponse.
    """
    try:
        # Formater le prompt
        formatted_prompt = prompt.format(
            dialect=db.dialect,
            table_info=db.get_table_info(),
            question=question,
        )

        # Exécuter l'agent
        config = {"configurable": {"thread_id": "1"}}
        response = agent_executor.invoke(
            {"messages": [HumanMessage(content=formatted_prompt)]}, config
        )
        
        # Le 2e message contient la requête exécutée
        query = response["messages"][1].tool_calls[0]["args"]["query"]
        
        # Le dernier message contient la réponse de l'agent
        answer = response["messages"][-1].content
        
        return query, answer

    except Exception as e:
        return f"Erreur : {e}"


# Interface Streamlit
st.title("Assistant SQL - Langage Naturel")

# Entrée de l'utilisateur pour la question
question = st.text_input("Posez votre question en langage naturel")

# Bouton pour soumettre la question
if st.button("Exécuter la requête"):
    if question:
        # Récupérer les résultats en appelant la fonction
        results = generate_sql_and_get_results(question)

        # Afficher les résultats sous forme de liste
        if len(results) == 2:
            query, answer = results
            st.write("Requête SQL générée")
            st.write("```\n" + query + "\n```")
            
            st.write("Résultats")
            st.write(answer)
        else:
            st.error(results)
    else:
        st.error("Veuillez entrer une question.")
