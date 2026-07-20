import argparse
from .models import ADUser

def parse_args():
    parser = argparse.ArgumentParser(description="AS-REP Roasting Audit Tool (Lab)")
    parser.add_argument("-u", "--users", required=True, help="File containing the list of users")
    parser.add_argument("-d", "--domain", required=True, help="Target domain (e.g. lab.local)")
    parser.add_argument("-dc-ip", "--dc-ip", required=True, help="Domain controller IP address")
    parser.add_argument("-o", "--output", default="report.txt", help="Final report file")
    parser.add_argument("--hashes", default="hashes.txt", help="Hashcat-compatible export file (mode 18200)")
    return parser.parse_args()

def interactive_selection(users: list[ADUser]) -> list[ADUser]:
    """Affiche les résultats et permet de sélectionner les utilisateurs à exporter"""
    roastable_users = [u for u in users if u.roastable]
    
    print("\n--- Enum results ---")
    for idx, user in enumerate(roastable_users):
        print(f"[{idx}] {user.username} - ROASTABLE")
        
    print("\nEnter the user numbers to export (separated by commas), or 'all' for all of them:")
    choice = input("> ").strip()
    
    if choice.lower() == 'all':
        return users
        
    selected_indices = [int(i.strip()) for i in choice.split(",") if i.strip().isdigit()]
    
    selected_users = []
    # On garde tous les utilisateurs pour le rapport final complet mais on marque seulement ceux selectionnes pour l'export de hash
    for user in users:
        if user in roastable_users and roastable_users.index(user) not in selected_indices:
            user.hash_value = None 
        selected_users.append(user)
            
    return selected_users
