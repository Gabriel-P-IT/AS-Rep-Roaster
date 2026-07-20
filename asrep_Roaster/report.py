from .models import ADUser

def generate_full_report(users: list[ADUser], output_file: str):
    """Génère le fichier texte avec les statuts"""
    with open(output_file, 'w', encoding='utf-8') as f:
        for user in users:
            if user.hash_value:
                f.write(f"[ROASTABLE] {user.username} - {user.hash_value[:30]}...\n")
            else:
                f.write(f"[X] {user.username} - no hash roastable\n")

def export_hashes(users: list[ADUser], hash_file: str):
    """Exporte les hashes au format Hashcat."""
    with open(hash_file, 'w', encoding='utf-8') as f:
        # Rappel pour le format etype 23
        f.write("# Format AS-REP Kerberos 5 etype 23 (Hashcat mode 18200)\n")
        for user in users:
            if user.hash_value:
                f.write(f"{user.get_hashcat_format()}\n")
