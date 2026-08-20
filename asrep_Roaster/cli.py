#!/usr/bin/env python3
import argparse
from .models import ADUser

def parse_args():
    parser = argparse.ArgumentParser(description="AS-REP Roasting Audit Tool (Lab)")
    # --- Users Source ---
    parser.add_argument("-u", "--users", default=None, help="File containing the list of users (omit when using --auto-discover)")
    # --- Target ---
    parser.add_argument("-d", "--domain", required=True, help="Target domain (e.g. lab.local)")
    parser.add_argument("-dc-ip", "--dc-ip", required=True, help="Domain controller IP address")
    # --- Auto-discovery ---
    parser.add_argument("--auto-discover", action="store_true", help="Discover domain user accounts via an LDAP query instead of supplying -u/--users (requires the 'ldap3' package)")
    parser.add_argument("--discover-user", default=None, help="Username for an authenticated LDAP bind during discovery (omit to attempt an anonymous bind)")
    parser.add_argument("--discover-password", default=None, help="Password for --discover-user")
    parser.add_argument("--discover-ldaps", action="store_true", help="Use LDAPS (port 636) instead of plaintext LDAP (389) for the discovery bind")
    # --- Report ---
    parser.add_argument("-o", "--output", default="report.txt", help="Final report file")
    parser.add_argument("--hashes", default="hashes.txt", help="Hashcat-compatible export file (mode 18200)")
    # --- Cracking ---
    parser.add_argument("--crack", action="store_true", help="Automatically crack exported hashes with hashcat (mode 18200)")
    parser.add_argument("--wordlist", default="/usr/share/wordlists/rockyou.txt", help="Wordlist path used for automatic cracking (default: rockyou.txt)")
    parser.add_argument("--rules", default=None, help="Optional hashcat rules file (e.g. best64.rule)")
    parser.add_argument("--crack-timeout", type=int, default=600, help="Max seconds allowed for the cracking phase (default: 600)")
    # --- Stealth ---
    parser.add_argument("--stealth", type=int, choices=[1, 2, 3, 4], default=None, help="Stealth mode (1=low to 4=paranoid). Adds delays, jitter and randomization between AS-REP requests.")
    # --- Enum Only ---
    parser.add_argument("--enum-only", action="store_true", help="Only enumerate vulnerable accounts (no hash export, no cracking). Outputs a clean list of roastable users.")

    args = parser.parse_args()

    # Sanity checks
    if args.enum_only and args.crack:
        parser.error("--enum-only and --crack are mutually exclusive.")

    if args.users and args.auto_discover:
        parser.error("-u/--users and --auto-discover are mutually exclusive.")

    if not args.users and not args.auto_discover:
        parser.error("Either -u/--users or --auto-discover is required.")

    if args.discover_password and not args.discover_user:
        parser.error("--discover-password requires --discover-user.")

    # When auto-discovering, this is where the discovered usernames get
    # written to, then re-loaded through the normal file-based flow.
    if args.auto_discover and not args.users:
        args.users = "discovered_users.txt"

    return args

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
    for user in users:
        if user in roastable_users and roastable_users.index(user) not in selected_indices:
            user.hash_value = None
        selected_users.append(user)

    return selected_users


def print_enum_only_results(users: list[ADUser]):
    """Affiche uniquement la liste des comptes roastables, sans hash."""
    roastable = [u for u in users if u.roastable]
    total = len(users)

    print("\n" + "=" * 50)
    print(f"  [ENUM-ONLY] Roastable accounts — {len(roastable)}/{total} users")
    print("=" * 50)

    if not roastable:
        print("  [-] No roastable account found.")
    else:
        for user in roastable:
            print(f"  [+] {user.username}")

    print("=" * 50)
    print("[*] No hash exported, no cracking performed (--enum-only mode).")
