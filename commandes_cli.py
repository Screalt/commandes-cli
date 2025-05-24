#!/usr/bin/env python3
import os
import json
import threading
import time
import re
import imaplib
import email
import tempfile
import subprocess
import traceback
from datetime import datetime

CONFIG_PATH = "config.json"
ORDERS_PATH = "orders.json"

# --- Gestion des commandes ---
class OrdersManager:
    def __init__(self, path):
        self.path = path
        self.orders = {}
        self._load()

    def _load(self):
        if os.path.exists(self.path):
            try:
                with open(self.path, encoding="utf-8") as f:
                    self.orders = json.load(f)
            except:
                self.orders = {}

    def _save(self):
        try:
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump(self.orders, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[{datetime.now().isoformat()}] Erreur sauvegarde orders:", e)

    def add_or_update(self, order):
        num = order["numero_commande"]
        now = time.time()
        order.setdefault("date_received", now)
        self.orders[num] = order
        self._save()
        return order

# --- Config ---
def load_config():
    if os.path.exists(CONFIG_PATH):
        try:
            return json.load(open(CONFIG_PATH, encoding="utf-8"))
        except:
            return {}
    return {}

def save_config(config):
    try:
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"[{datetime.now().isoformat()}] Erreur sauvegarde config:", e)

# --- Parsing commandes ---
def parse_order(text):
    text = re.sub(r"<https?://[^>]+>", "", text)
    if "<html" in text.lower():
        text = re.sub(r"(?i)<br\s*/?>", "\n", text)
        text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"https?://\S+", "", text)

    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    num = None
    for ln in lines:
        m = re.match(r"Nouvelle commande #(\d+)", ln)
        if m:
            num = m.group(1)
            break
    if not num:
        return None

    formatted_lines = [f"Commande #{num} — {datetime.now().isoformat()}"]
    formatted_lines += [f"- {ln}" for ln in lines]
    formatted = "\n".join(formatted_lines)

    return {"numero_commande": num, "formatted_text": formatted}

# --- Impression via CUPS ---
def imprimer_commande(order, printer_name=None):
    text = order.get("formatted_text", "")
    if not text:
        print(f"[{datetime.now().isoformat()}] Aucun texte à imprimer.")
        return
    with tempfile.NamedTemporaryFile(delete=False, suffix=".txt", mode="w", encoding="utf-8") as tmp:
        tmp.write(text)
        fn = tmp.name
    cmd = ["lpr"]
    if printer_name:
        cmd += ["-P", printer_name]
    cmd.append(fn)
    try:
        subprocess.run(cmd, check=True)
        print(f"[{datetime.now().isoformat()}] Impression envoyée à « {printer_name or 'défaut'} ».")
    except subprocess.CalledProcessError as e:
        print(f"[{datetime.now().isoformat()}] Erreur impression :", e)

# --- Polling IMAP ---
class EmailPoller(threading.Thread):
    def __init__(self, config, mgr):
        super().__init__(daemon=True)
        self.config = config
        self.mgr = mgr
        self._stop = threading.Event()

    def run(self):
        print(f"[{datetime.now().isoformat()}] Polling IMAP démarré.")
        while not self._stop.is_set():
            c = self.config
            # Vérifie qu'on a les infos indispensables
            if all(c.get(k) for k in ("imap_server","imap_port","email_address","email_password")):
                try:
                    print(f"[{datetime.now().isoformat()}] Connexion à {c['imap_server']}:{c['imap_port']}…")
                    M = imaplib.IMAP4_SSL(c["imap_server"], int(c["imap_port"]))
                    M.login(c["email_address"], c["email_password"])
                    print(f"[{datetime.now().isoformat()}] Connexion IMAP réussie.")
                    M.select("INBOX")

                    # Critères de recherche
                    crit = ["UNSEEN"]
                    if c.get("filter_sender"):
                        crit += ["FROM", f'"{c["filter_sender"]}"']
                    if c.get("filter_subject"):
                        crit += ["SUBJECT", f'"{c["filter_subject"]}"']
                    print(f"[{datetime.now().isoformat()}] Recherche mails avec critères : {crit}")
                    typ, data = M.search(None, *crit)
                    if typ != "OK":
                        print(f"[{datetime.now().isoformat()}] Recherche IMAP a échoué : {typ}")
                    else:
                        ids = data[0].split()
                        if not ids:
                            print(f"[{datetime.now().isoformat()}] Aucun nouveau mail.")
                        for num in ids:
                            print(f"[{datetime.now().isoformat()}] Nouveau mail ID {num.decode()}.")
                            _, md = M.fetch(num, "(RFC822)")
                            msg = email.message_from_bytes(md[0][1])
                            raw = ""
                            if msg.is_multipart():
                                for part in msg.walk():
                                    if part.get_content_type() == "text/plain":
                                        raw = part.get_payload(decode=True).decode(errors="ignore")
                                        break
                            else:
                                raw = msg.get_payload(decode=True).decode(errors="ignore")

                            parsed = parse_order(raw)
                            if parsed:
                                self.mgr.add_or_update(parsed)
                                print("---------------------------")
                                print(parsed["formatted_text"])
                                imprimer_commande(parsed, printer_name=c.get("printer_name"))
                            else:
                                print(f"[{datetime.now().isoformat()}] Mail ignoré (pas de numéro de commande trouvé).")
                            M.store(num, "+FLAGS", "\\Seen")
                    M.logout()
                except Exception as e:
                    print(f"[{datetime.now().isoformat()}] IMAP error:")
                    traceback.print_exc()
            else:
                print(f"[{datetime.now().isoformat()}] Configuration IMAP incomplète : {c}")
            time.sleep(int(c.get("poll_interval", 60)))
        print(f"[{datetime.now().isoformat()}] Polling IMAP arrêté.")

    def stop(self):
        self._stop.set()

# --- Menu CLI ---
def cli_menu():
    config = load_config()
    mgr = OrdersManager(ORDERS_PATH)

    while True:
        print("\n--- MENU ---")
        print("1) Paramétrer")
        print("2) Lancer le service")
        print("3) Quitter")
        choice = input("Votre choix : ").strip()

        if choice == '1':
            for key in ("imap_server","imap_port","email_address","email_password",
                        "filter_sender","filter_subject","poll_interval","printer_name"):
                current = config.get(key, "")
                val = input(f"{key} [{current}]: ").strip()
                if val:
                    config[key] = val
            save_config(config)
            print(f"[{datetime.now().isoformat()}] Configuration enregistrée.")
        elif choice == '2':
            print(f"[{datetime.now().isoformat()}] Démarrage du service… (Ctrl+C pour arrêter)")
            poller = EmailPoller(config, mgr)
            poller.start()
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print(f"\n[{datetime.now().isoformat()}] Arrêt du service par l’utilisateur.")
                poller.stop()
                break
        elif choice == '3':
            print(f"[{datetime.now().isoformat()}] Au revoir !")
            break
        else:
            print("Choix invalide.")

if __name__ == "__main__":
    cli_menu()
