import os
import requests
import yaml
import sys
from dotenv import load_dotenv

load_dotenv()

# Environment
NPM_URL = os.getenv("NPM_URL")
NPM_EMAIL = os.getenv("NPM_EMAIL")
NPM_PASSWORD = os.getenv("NPM_PASSWORD")

PIHOLE_URL = os.getenv("PIHOLE_URL")
PIHOLE_API_TOKEN = os.getenv("PIHOLE_API_TOKEN")
PROXY_CNAME_TARGET = os.getenv("PROXY_CNAME_TARGET")

OUTPUT_FILE = os.getenv("OUTPUT_FILE", "services-npm.yaml")
HOMEPAGE_GROUP = os.getenv("HOMEPAGE_GROUP", "Reverse Proxies")

if not all([NPM_URL, NPM_EMAIL, NPM_PASSWORD]):
    print("✖ Missing NPM credentials in .env")
    sys.exit(1)

# Sessions
npm = requests.Session()
npm.verify = True

# NPM Functions
def npm_login():
    r = npm.post(
        f"{NPM_URL}/api/tokens",
        json={"identity": NPM_EMAIL, "secret": NPM_PASSWORD},
        timeout=10,
    )
    r.raise_for_status()
    token = r.json()["token"]
    npm.headers.update({"Authorization": f"Bearer {token}"})


def get_proxy_hosts():
    r = npm.get(f"{NPM_URL}/api/nginx/proxy-hosts", timeout=10)
    r.raise_for_status()
    return r.json()


# Homepage YAML
def build_homepage_services(proxies):
    group = {}

    for proxy in proxies:
        if not proxy.get("enabled", False):
            continue

        description = (
            proxy.get("meta", {}).get("name")
            or f"{proxy.get('forward_host')}:{proxy.get('forward_port')}"
            or "Proxy"
        )

        for domain in proxy.get("domain_names", []):
            group[domain] = {
                "href": f"https://{domain}",
                "description": description,
            }

    return [{HOMEPAGE_GROUP: group}]


def write_yaml(data):
    with open(OUTPUT_FILE, "w") as f:
        yaml.dump(data, f, sort_keys=False)


# Pi-hole DNS
def pihole_add_cname(domain):
    if not all([PIHOLE_URL, PIHOLE_API_TOKEN, PROXY_CNAME_TARGET]):
        return

    r = requests.get(
        f"{PIHOLE_URL}/admin/api.php",
        params={
            "customdns": "",
            "action": "add",
            "domain": domain,
            "ip": PROXY_CNAME_TARGET,
            "type": "CNAME",
            "auth": PIHOLE_API_TOKEN,
        },
        timeout=5,
    )

    # Pi-hole returns success even if it already exists
    if r.status_code != 200:
        print(f"⚠ Pi-hole failed for {domain}")


def sync_pihole(proxies):
    for proxy in proxies:
        if not proxy.get("enabled", False):
            continue

        for domain in proxy.get("domain_names", []):
            pihole_add_cname(domain)

def main():
    try:
        npm_login()
        proxies = get_proxy_hosts()

        services = build_homepage_services(proxies)
        write_yaml(services)

        sync_pihole(proxies)

        print(f"✔ Homepage updated: {OUTPUT_FILE}")
        print("✔ Pi-hole CNAME sync complete")

    except Exception as e:
        print(f"✖ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
