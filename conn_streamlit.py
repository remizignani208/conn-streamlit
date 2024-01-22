import streamlit as st
import sqlite3
from passlib.hash import pbkdf2_sha256

# Fonction pour créer la table dans la base de données si elle n'existe pas
def create_table():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            prenom TEXT,
            nom TEXT,
            email TEXT UNIQUE,
            password TEXT
        )
    """)
    conn.commit()
    conn.close()

# Fonction pour enregistrer un nouvel utilisateur dans la base de données
def register_user(prenom, nom, email, password):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    # Hash du mot de passe avant de le stocker dans la base de données
    hashed_password = pbkdf2_sha256.hash(password)

    cursor.execute("""
        INSERT INTO users (prenom, nom, email, password)
        VALUES (?, ?, ?, ?)
    """, (prenom, nom, email, hashed_password))

    conn.commit()
    conn.close()

    st.success(f"Utilisateur enregistré : \n Prénom: {prenom} \n Nom: {nom} \n Email: {email}")

# Fonction pour connecter un utilisateur existant
def login_user(email, password):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    # Récupération du mot de passe stocké dans la base de données
    cursor.execute("SELECT password FROM users WHERE email=?", (email,))
    result = cursor.fetchone()

    if result is not None:
        hashed_password = result[0]
        # Vérification du mot de passe
        if pbkdf2_sha256.verify(password, hashed_password):
            st.session_state.user_logged_in = True
            st.success(f"Connecté en tant que : {email}")
            return True  # Utilisateur connecté
        else:
            st.error("Mot de passe incorrect.")
    else:
        st.error("Adresse e-mail non enregistrée.")

    conn.close()
    st.session_state.user_logged_in = False
    return False  # Utilisateur non connecté

# Fonction pour afficher les données de la base de données
def display_database():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, prenom, nom, email FROM users")
    data = cursor.fetchall()
    conn.close()

    st.title("Base de données utilisateurs")
    st.table(data)

def delete_user(email):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    cursor.execute("DELETE FROM users WHERE email=?", (email,))

    conn.commit()
    conn.close()

    st.success("La suppression a été effectuée avec succès.")
    st.experimental_rerun()

# Fonction de déconnexion
def logout():
    st.session_state.user_logged_in = False
    st.warning("Vous avez été déconnecté.")

# Initialiser la session avec la création de la table
create_table()

# Définir la page d'inscription
def register_page():
    st.title("Page d'inscription")
    prenom = st.text_input("Prénom")
    nom = st.text_input("Nom")
    email = st.text_input("Adresse e-mail")
    password = st.text_input("Mot de passe", type="password")

    # Condition pour le mot de passe
    if len(password) < 8:
        st.warning("Le mot de passe doit contenir au moins 8 caractères.")

    if st.button("S'inscrire") and len(password) >= 8:
        register_user(prenom, nom, email, password)

# Définir la page de connexion
def login_page():
    st.title("Page de connexion")
    email = st.text_input("Adresse e-mail")
    password = st.text_input("Mot de passe", type="password")

    if st.button("Se connecter"):
        login_user(email, password)

# Définir la page de suppression
def delete_page():
    st.title("Page de suppression")
    email_to_delete = st.text_input("Entrez l'adresse e-mail à supprimer")

    if st.button("Supprimer"):
        delete_user(email_to_delete)

# Définir la page de déconnexion
def logout_page():
    st.title("Page de déconnexion")
    st.write("Êtes-vous sûr de vouloir vous déconnecter?")
    if st.button("Déconnexion"):
        logout()

# Barre de navigation pour basculer entre les pages
page = st.sidebar.radio("Navigation", ["Inscription", "Connexion", "Suppression", "Base de données", "Déconnexion"])

# Affichage de la page appropriée en fonction de la sélection
if page == "Inscription":
    register_page()
elif page == "Connexion":
    login_page()
elif page == "Suppression":
    delete_page()
elif page == "Base de données" and st.session_state.get("user_logged_in", False):
    display_database()
elif page == "Base de données" and not st.session_state.get("user_logged_in", False):
    st.warning("Vous devez vous connecter pour accéder à la base de données.")
elif page == "Déconnexion":
    logout_page()
