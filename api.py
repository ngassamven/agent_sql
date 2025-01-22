import sqlite3
import streamlit as st
from langchain_community.utilities import SQLDatabase
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

# Connexion à la base de données SQLite
connection = sqlite3.connect("mydb.db")
cusor = connection.cursor()

# API Key pour ChatGroq
api_key = "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"

# Initialiser ChatGroq avec la clé API
llm = ChatGroq(model="llama3-8b-8192", api_key=api_key)

# Créer une instance SQLDatabase
db = SQLDatabase.from_uri("sqlite:///mydb.db")


# Fonction pour générer une requête SQL et obtenir les résultats
def generate_sql_and_get_results(query: str) -> list:
    """
    Utilise le modèle LLM pour convertir une question en langage naturel en une requête SQL,
    puis exécute cette requête et retourne les résultats sous forme de liste.
    """
    try:
        # Générer la requête SQL à partir de la question en langage naturel
        response = llm.invoke(f"Convertir cette question en requête SQL valide : {query}")

        # Extraire la requête SQL générée par le modèle
        sql_query = response.content.strip()  # Assurer qu'il n'y a pas de texte supplémentaire

        # Afficher la requête SQL générée pour débogage
        st.write(f"Requête SQL générée : {sql_query}")

        # Exécuter la requête SQL
        result = db.run(sql_query)

        # Retourner les résultats sous forme de liste
        if isinstance(result, list):
            return result
        else:
            return [{"error": "Résultat non sous forme de liste"}]

    except Exception as e:
        st.error(f"Erreur lors de l'exécution de la requête : {e}")
        return [{"error": f"Erreur : {str(e)}"}]


# Interface Streamlit
st.title("Assistant SQL - Langage Naturel")

# Entrée de l'utilisateur pour la question
query = st.text_input("Posez votre question en langage naturel:")

# Bouton pour soumettre la question
if st.button("Exécuter la requête"):
    if query:
        # Récupérer les résultats en appelant la fonction
        results = generate_sql_and_get_results(query)

        # Afficher les résultats sous forme de liste
        if results:
            st.write("Résultats de la requête :")
            st.write(results)
    else:
        st.error("Veuillez entrer une question.")
