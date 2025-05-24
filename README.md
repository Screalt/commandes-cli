# commandes-cli

Client CLI Python pour récupérer, afficher et imprimer automatiquement vos commandes reçues par e-mail.

---

## 🚀 Fonctionnalités

- Connexion IMAP pour récupérer les nouveaux e-mails de commande  
- Parsing des messages (HTML ou texte) pour extraire :
  - Numéro de commande  
  - Date  
  - Articles (nom, quantité, prix unitaire, total)  
  - Totaux et sous-totaux  
  - Informations client  
- Affichage de chaque commande dans la console, séparée par :
  ```bash
  ---------------------------

    Impression automatique via CUPS (lpr) — compatible ticket thermique

    Configuration simple via variables d’environnement (.env) ou fichier config.json

    Installation et mise à jour en une seule commande depuis GitHub

📦 Installation

    Mettre à jour votre système et installer les dépendances

sudo apt update
sudo apt install -y python3 python3-pip python3-tk cups python3-cups

Installer le package depuis GitHub

pip3 install --upgrade git+https://github.com/Screalt/commandes-cli.git

Créer le fichier de configuration .env

cp .env.example .env
nano .env

Puis adaptez son contenu :

    IMAP_SERVER=imap.votre-fournisseur.com
    IMAP_PORT=993
    EMAIL_ADDRESS=votre.email@example.com
    EMAIL_PASS=VotreMotDePasseApp
    PRINTER_NAME=NomDeVotreImprimante
    POLL_INTERVAL=60

🛠️ Usage

Lancez la commande :

commandes-cli

Vous verrez alors un menu :

    Paramétrer
    Saisissez ou modifiez les variables IMAP, imprimante et intervalle de polling.

    Démarrer le service

        Connexion en boucle à votre boîte IMAP

        Affichage de chaque nouvelle commande, séparée par :

        ---------------------------

        Impression automatique via CUPS

        Marquage des mails comme lus

    Quitter
    Pour arrêter le service proprement ou via Ctrl+C.

🔄 Mise à jour

Pour récupérer la dernière version :

pip3 install --upgrade git+https://github.com/Screalt/commandes-cli.git

📄 Licence

© 2025 Screalt
Distribué sous la MIT License – voir LICENSE pour plus de détails.
🙏 Crédits

Si vous utilisez ce projet, merci de me créditer en mentionnant ce dépôt :

https://github.com/Screalt/commandes-cli
