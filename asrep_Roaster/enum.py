#!/usr/bin/python3
import os
from .models import ADUser

def load_users(filepath: str) -> list[ADUser]:
    """Charge une liste d'utilisateurs depuis un fichier txt"""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"The file {filepath} is not found")
        
    users = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            username = line.strip()
            if username:
                users.append(ADUser(username=username))
    return users


def save_users(usernames: list[str], filepath: str) -> None:
    """Écrit une liste de noms d'utilisateurs dans un fichier texte, un par ligne."""
    with open(filepath, 'w', encoding='utf-8') as f:
        for username in usernames:
            f.write(username + "\n")
