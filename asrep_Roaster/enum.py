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
