# commandes-cli

Client CLI Python pour récupérer, afficher et imprimer automatiquement vos commandes reçues par e-mail.

---

## 🚀 Fonctionnalités

- Connexion IMAP pour récupérer les nouveaux e-mails de commande  
- Parsing des messages (HTML ou texte) pour extraire numéro, date, articles, totaux, client  
- Affichage de chaque commande dans la console, séparée par  


- Impression automatique via CUPS (`lpr`) sur imprimante ticket thermique ou autre  
- Configuration simple via variables d’environnement (`.env`) ou `config.json`  
- Installation et mise à jour en une seule commande depuis GitHub  

---

## 📦 Installation

1. Installez Python 3, Tkinter et CUPS :
 ```bash
 sudo apt update
 sudo apt install -y python3-pip python3-tk cups python3-cups


Installez le package directement depuis GitHub :

pip3 install git+https://github.com/VOTRE_COMPTE/commandes-cli.git

IMAP_SERVER=imap.votre-fournisseur.com
IMAP_PORT=993
EMAIL_ADDRESS=votre.email@example.com
EMAIL_PASS=VotreMotDePasseApp
PRINTER_NAME=NomDeVotreImprimante
POLL_INTERVAL=60


## 🛠️ Usage

Lancez simplement :

commandes-cli
