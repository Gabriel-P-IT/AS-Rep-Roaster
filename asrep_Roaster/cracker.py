import os
import shutil
import subprocess
import logging

from .models import ADUser

logger = logging.getLogger(__name__)

HASHCAT_BIN = "hashcat"
HASHCAT_MODE = "18200"
POTFILE = "asrep_roaster.potfile"


def check_hashcat_available() -> bool:
    """Check if hashcat is available in PATH."""
    if shutil.which(HASHCAT_BIN) is None:
        logger.error(f"[-] '{HASHCAT_BIN}' not found in PATH. Install hashcat first.")
        return False
    return True


def run_hashcat(
    hash_file: str,
    wordlist: str,
    rules_file: str = None,
    timeout: int = 600
) -> bool:
    """
    Runs hashcat against the exported hash file using the given wordlist.
    Uses a dedicated potfile to avoid mixing results with other campaigns.
    """
    if not check_hashcat_available():
        return False

    if not os.path.exists(hash_file):
        logger.error(f"[-] Hash file not found: {hash_file}")
        return False

    if not os.path.exists(wordlist):
        logger.error(f"[-] Wordlist not found: {wordlist}")
        return False

    cmd = [
        HASHCAT_BIN,
        "-m", HASHCAT_MODE,
        hash_file,
        wordlist,
        "--potfile-path", POTFILE,
        "--force",
    ]

    if rules_file:
        if not os.path.exists(rules_file):
            logger.warning(f"[!] Rules file not found, ignoring: {rules_file}")
        else:
            cmd += ["-r", rules_file]

    logger.info(f"[*] Running: {' '.join(cmd)}")

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout
        )
    except subprocess.TimeoutExpired:
        logger.warning(f"[!] Hashcat timed out after {timeout}s (partial results may exist in potfile)")
        return True  # potfile may still contain partial cracks
    except FileNotFoundError:
        logger.error(f"[-] Command not found: {HASHCAT_BIN}")
        return False

    if result.returncode not in (0, 1):
        # hashcat returns 1 when exhausted without full success — not fatal
        logger.warning(f"[!] Hashcat exited with code {result.returncode}")
        if result.stderr:
            logger.warning(f"[!] stderr: {result.stderr.strip()}")

    return True


def parse_cracked_passwords(users: list[ADUser]) -> int:
    """
    Reads the hashcat potfile and maps cracked passwords back to
    their corresponding ADUser objects. Returns the number cracked.
    """
    if not os.path.exists(POTFILE):
        logger.warning("[!] No potfile found, nothing was cracked")
        return 0

    cracked_count = 0

    with open(POTFILE, "r", encoding="utf-8", errors="ignore") as f:
        lines = [line.strip() for line in f if line.strip()]

    for line in lines:
        # Potfile format: <full_hash>:<password>
        # The hash itself contains internal colons (krb5asrep format),
        # so we must split on the LAST colon only.
        if ":" not in line:
            continue

        hash_part, password = line.rsplit(":", 1)

        for user in users:
            if user.hash_value and hash_part in user.hash_value:
                user.cracked_password = password
                cracked_count += 1
                logger.info(f"[+] Cracked: {user.username} -> {password}")
                break

    return cracked_count


def crack_hashes(
    users: list[ADUser],
    hash_file: str,
    wordlist: str,
    rules_file: str = None,
    timeout: int = 600
) -> None:
    """
    Full pipeline: run hashcat, then parse and hydrate cracked passwords
    into the corresponding ADUser objects.
    """
    roastable_users = [u for u in users if u.roastable and u.hash_value]

    if not roastable_users:
        logger.warning("[!] No roastable users with hashes to crack")
        return

    logger.info(f"[*] Starting automatic cracking on {len(roastable_users)} hash(es)")

    success = run_hashcat(hash_file, wordlist, rules_file, timeout)

    if not success:
        logger.error("[-] Cracking failed, no passwords retrieved")
        return

    count = parse_cracked_passwords(users)
    logger.info(f"[+] Cracking complete: {count}/{len(roastable_users)} password(s) recovered")

    if os.path.exists(POTFILE):
        os.remove(POTFILE)
