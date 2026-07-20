# AS-Rep-Roaster

Outil Python d'audit Active Directory orienté AS-REP Roasting, conçu pour un usage pédagogique dans un environnement de lab autorisé.

Ce projet automatise la détection de comptes Active Directory vulnérables à l'AS-REP Roasting (comptes avec la pré-authentification Kerberos désactivée), récupère les hashes exploitables via l'outil `impacket-GetNPUsers`, puis génère un rapport et un export compatible Hashcat.

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
- Génération d'un rapport texte final
- Export séparé des hashes au format compatible Hashcat (mode **18200** pour etype 23)

---

## Architecture

AS-Rep-Roaster/
├── README.md
├── requirements.txt
├── Roaster.py
└── asrep_Roaster/
  ├── models.py # Modèle de données ADUser
  ├── enum.py # Chargement et traitement de la liste d'utilisateurs
  ├── asrep.py # Wrapper subprocess autour d'impacket-GetNPUsers
  ├── report.py # Génération des fichiers de sortie
  └── cli.py # Argparse et interface terminal interactive

  ## Installation

```bash
git clone https://github.com/Gabriel-P-IT/AS-Rep-Roaster.git
cd AS-Rep-Roaster
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Utilisation

```bash
python3 Roaster.py -h

usage: Roaster.py [-h] -u USERS -d DOMAIN -dc-ip DC_IP [-o OUTPUT] [--hashes HASHES]

AS-REP Roasting Audit Tool (Lab)

options:
-h, --help show this help message and exit
-u, --users USERS File containing the list of users
-d, --domain DOMAIN Target domain (e.g. lab.local)
-dc-ip, --dc-ip DC_IP
Domain controller IP address
-o, --output OUTPUT Final report file
--hashes HASHES Hashcat-compatible export file (mode 18200)
```

## Cracking avec Hashcat

```bash
hashcat -m 18200 hash.txt /usr/share/wordlists/rockyou.txt
```

## Avertissement légal

Cet outil est fourni à des fins **strictement éducatives et pédagogiques**, dans le cadre d'un projet scolaire de cybersécurité offensive. Il ne doit être utilisé que contre :

- des environnements de lab que vous possédez ou que vous êtes explicitement autorisé à tester;
- des systèmes couverts par un accord de test d'intrusion en règle (scope + autorisation écrite).

Toute utilisation contre un système sans autorisation explicite est illégale et constitue une infraction pénale. L'auteur de ce projet ne pourra être tenu responsable d'un usage détourné de cet outil.


## Roadmap — Améliorations futures

### Cracking automatique intégré

- Ajouter une option `--crack` déclenchant automatiquement Hashcat en mode 18200 (ou 17600/18200 selon l'etype détecté) directement après l'export, sans étape manuelle.
- Intégrer un wordlist par défaut configurable (`--wordlist rockyou.txt`) avec détection de présence du fichier avant lancement.
- Afficher en fin de rapport les mots de passe cassés en clair, associés au bon utilisateur, dans une section dédiée `[CRACKED]`.
- Ajouter un mode `--rules` pour appliquer des règles Hashcat (best64.rule, OneRuleToRuleThemAll) et augmenter le taux de succès sur des mots de passe proches d'un dictionnaire.
- Gérer un timeout ou un budget de temps de cracking configurable, pour éviter un blocage indéfini sur un gros wordlist.

### Discrétion accrue de l'énumération

- Ajouter des paramètres `--delay` et `--jitter` pour espacer aléatoirement les requêtes AS-REQ envoyées, réduisant le nombre d'événements Windows 4768 générés dans une fenêtre de temps courte.
- Introduire un mode `--batch-size` pour tester les utilisateurs par petits lots plutôt qu'en une seule vague, avec pause entre chaque lot.
- Supporter la randomisation de l'ordre des utilisateurs testés (`--shuffle`), pour casser la logique de scan séquentiel visible côté SIEM.
- Ajouter une option `--single-etype` pour ne demander qu'un seul type de chiffrement à la fois (au lieu de RC4 + AES en cascade), limitant la signature réseau de l'outil.
- Documenter dans le rapport final le nombre de requêtes envoyées et leur étalement temporel, pour illustrer pédagogiquement l'impact du delay/jitter sur la détectabilité.
