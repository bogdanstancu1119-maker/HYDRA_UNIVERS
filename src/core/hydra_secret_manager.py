import os, re, time, base64, imaplib, email, requests
from nacl import encoding, public

GH_PAT = os.getenv("GH_PAT")
GH_REPO = os.getenv("GH_REPO")
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")

def pune_secret_github(nume, valoare):
    print(f"Pun secret {nume} in {GH_REPO}")
    h = {"Authorization": f"token {GH_PAT}", "Accept": "application/vnd.github.v3+json"}
    r = requests.get(f"https://api.github.com/repos/{GH_REPO}/actions/secrets/public-key", headers=h)
    r.raise_for_status()
    kd = r.json()
    pk = public.PublicKey(kd["key"].encode(), encoding.Base64Encoder())
    sealed = public.SealedBox(pk)
    enc = sealed.encrypt(valoare.encode())
    b64 = base64.b64encode(enc).decode()
    rr = requests.put(f"https://api.github.com/repos/{GH_REPO}/actions/secrets/{nume}", headers=h, json={"encrypted_value": b64, "key_id": kd["key_id"]})
    print(f"Secret {nume} status {rr.status_code}")
    return rr.status_code in [201,204]

def citeste_email_si_extra_token():
    print(f"Conectare IMAP la {EMAIL_USER}")
    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    mail.login(EMAIL_USER, EMAIL_PASS)
    mail.select("INBOX")
    # cauta ultimele 10 emailuri necitite
    _, data = mail.search(None, 'UNSEEN')
    ids = data[0].split()[-10:]
    for eid in reversed(ids):
        _, msg_data = mail.fetch(eid, '(RFC822)')
        msg = email.message_from_bytes(msg_data[0][1])
        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    body += part.get_payload(decode=True).decode(errors="ignore")
        else:
            body = msg.get_payload(decode=True).decode(errors="ignore")
        # cauta link de confirmare
        links = re.findall(r'https?://[^\s"\']+confirm[^\s"\']+|https?://[^\s"\']+verify[^\s"\']+', body)
        for link in links:
            print(f"Confirm link gasit: {link[:80]}")
            try: requests.get(link, timeout=15)
            except: pass
        # cauta token API - Vercel, Render, Fly etc
        m = re.search(r'(vercel_[a-zA-Z0-9_]+|rnd_[a-zA-Z0-9]+|fo1_[a-zA-Z0-9_\-]+|[A-Z0-9]{24,})', body)
        if m:
            token = m.group(1)
            print(f"Token gasit: {token[:10]}...")
            # marcheaza citit
            mail.store(eid, '+FLAGS', '\\Seen')
            mail.logout()
            return token, body
    mail.logout()
    return None, None

def main():
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--actiune", required=True)
    a = p.parse_args()
    if a.actiune == "cere_token":
        print("Hydra cauta email cu token...")
        for i in range(12): # asteapta 6 minute, polling la 30 sec
            token, body = citeste_email_si_extra_token()
            if token:
                # decide numele secretului dupa continut
                nume = "VERCEL_TOKEN"
                if "render" in body.lower(): nume = "RENDER_TOKEN"
                if "fly" in body.lower(): nume = "FLY_API_TOKEN"
                pune_secret_github(nume, token)
                print(f"GATA - {nume} pus autonom in secrete")
                return
            print(f"Incerc {i+1}/12 - mai astept 30s...")
            time.sleep(30)
        print("Niciun token in email. Trimite manual cerere de token pe emailul hydra si ruleaza din nou workflow.")
    elif a.actiune == "deploy":
        print("Deploy - token deja in secrete, fac deploy...")
        # aici intra comanda ta reala de deploy, deja are token din secrete
        os.system("npx vercel --prod --yes || echo 'vercel nu e configurat, dar secretul e pus'")

if __name__ == "__main__":
    main()
