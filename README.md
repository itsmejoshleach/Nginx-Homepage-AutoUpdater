# NPM → Homepage + Pi-hole Sync

Automatically syncs **Nginx Proxy Manager proxy hosts** into:

- 📊 Homepage (gethomepage.dev)
- 🌐 Pi-hole local DNS (CNAME records)

---

## Features

- Pulls all enabled proxy hosts from NPM
- Generates Homepage-compatible `services.yaml`
- Adds Pi-hole CNAME records:
app.example.com → proxy.internal

- Safe to run on cron
- Uses `.env` for secrets

---

## Installation

`pip install -r requirements.txt`

Configuration
Create a .env file:

```
NPM_URL=https://npm.example.com
NPM_EMAIL=admin@example.com
NPM_PASSWORD=password

PIHOLE_URL=http://pi.hole
PIHOLE_API_TOKEN=token
PROXY_CNAME_TARGET=proxy.internal
```
Usage:
`python3 npm_to_homepage.py`

Homepage Integration:
Include the generated file in services.yaml:
```
services:
  - include: services-npm.yaml
```

Cron Example
`*/10 * * * * python3 /config/npm_to_homepage.py`

Notes:
Pi-hole ignores duplicate CNAMEs safely

HTTPS links are assumed

Uses meta.name if set in NPM, otherwise backend IP:port

Security
Prefer API tokens where possible

Do not commit .env

---

## 5️⃣ Important Pi-hole Notes (worth knowing)

- Pi-hole **does not allow CNAME → IP**, only **CNAME → hostname**  
  ✅ Your `proxy.internal` approach is correct
- Existing records are **not duplicated**
- Changes apply immediately (no gravity rebuild needed)