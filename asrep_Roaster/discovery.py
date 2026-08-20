#!/usr/bin/env python3
"""
LDAP-based user auto-discovery.

Queries the target Domain Controller over LDAP to enumerate account
names (sAMAccountName) instead of requiring a pre-built username file.
Supports an anonymous bind (if allowed on the DC) or an authenticated
bind with low-privilege credentials.
"""
import logging

logger = logging.getLogger(__name__)

try:
    from ldap3 import Server, Connection, ALL, NTLM, SIMPLE
    LDAP3_AVAILABLE = True
except ImportError:
    LDAP3_AVAILABLE = False

# Excludes disabled accounts (userAccountControl bit 0x2 = ACCOUNTDISABLE)
LDAP_USER_FILTER = (
    "(&(objectCategory=person)(objectClass=user)"
    "(!(userAccountControl:1.2.840.113556.1.4.803:=2)))"
)


def domain_to_base_dn(domain: str) -> str:
    """Converts 'lab.local' into 'DC=lab,DC=local'."""
    return ",".join(f"DC={part}" for part in domain.split("."))


def discover_users(
    dc_ip: str,
    domain: str,
    username: str = None,
    password: str = None,
    use_ldaps: bool = False,
    timeout: int = 10,
) -> list[str]:
    """
    Enumerates sAMAccountName of enabled user accounts via LDAP.

    Tries an anonymous bind if no credentials are supplied. On any
    connection or search failure, logs the error and returns an empty
    list so the caller can decide how to proceed.
    """
    if not LDAP3_AVAILABLE:
        logger.error(
            "[-] ldap3 is required for --auto-discover. Install it with: pip install ldap3"
        )
        return []

    base_dn = domain_to_base_dn(domain)
    server = Server(
        dc_ip,
        port=636 if use_ldaps else 389,
        use_ssl=use_ldaps,
        get_info=ALL,
        connect_timeout=timeout,
    )

    try:
        if username:
            bind_user = f"{domain}\\{username}"
            conn = Connection(server, user=bind_user, password=password, authentication=NTLM, auto_bind=True)
            logger.info(f"[*] LDAP bind as {bind_user}@{dc_ip}")
        else:
            conn = Connection(server, authentication=SIMPLE, auto_bind=True)
            logger.info(f"[*] Anonymous LDAP bind to {dc_ip}")
    except Exception as exc:
        logger.error(f"[-] LDAP bind failed against {dc_ip}: {exc}")
        return []

    try:
        conn.search(
            search_base=base_dn,
            search_filter=LDAP_USER_FILTER,
            attributes=["sAMAccountName"],
        )
    except Exception as exc:
        logger.error(f"[-] LDAP search failed against base DN '{base_dn}': {exc}")
        conn.unbind()
        return []

    usernames = sorted({
        entry.sAMAccountName.value
        for entry in conn.entries
        if entry.sAMAccountName.value
    })

    conn.unbind()

    logger.info(f"[+] Discovered {len(usernames)} user account(s) via LDAP")
    return usernames
