#!/usr/bin/env python3
from .models import ADUser

def generate_full_report(users: list, output_file: str):
    """Generates the report file with ROASTABLE / X / CRACKED statuses."""
    with open(output_file, 'w', encoding='utf-8') as f:
        for user in users:
            if user.hash_value:
                f.write(f"[ROASTABLE] {user.username} - {user.hash_value[:30]}...\n")
            else:
                f.write(f"[X] {user.username} - No exploitable hash\n")

        cracked_users = [u for u in users if getattr(u, 'cracked_password', None)]
        if cracked_users:
            f.write("\n--- Cracked passwords ---\n")
            for user in cracked_users:
                f.write(f"[CRACKED] {user.username} : {user.cracked_password}\n")

def export_hashes(users: list[ADUser], hash_file: str):
    """Exporte les hashes au format Hashcat."""
    with open(hash_file, 'w', encoding='utf-8') as f:
        for user in users:
            if user.hash_value:
                f.write(f"{user.get_hashcat_format()}\n")
                
