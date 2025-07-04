import os
import yaml
from dotenv import load_dotenv

# Load .env
load_dotenv(dotenv_path=".env")

# Helper to get all env vars from .env
env_vars = dict(os.environ)

# Check docker-compose.yml
with open("docker-compose.yml") as f:
    compose = yaml.safe_load(f)

compose_vars = set()
for service in compose.get("services", {}).values():
    # Check image, container_name, environment, labels, volumes, ports
    for key in ["image", "container_name"]:
        val = service.get(key)
        if isinstance(val, str) and "${" in val:
            compose_vars.update([v[2:-1] for v in val.split() if v.startswith("${")])
    for section in ["environment", "labels", "volumes", "ports"]:
        for item in service.get(section, []) or []:
            if isinstance(item, str) and "${" in item:
                for part in item.split():
                    if part.startswith("${"):
                        compose_vars.add(part[2:-1].split('}')[0])

# Check traefik/traefik.yml
with open("traefik/traefik.yml") as f:
    traefik = f.read()
traefik_vars = set()
for line in traefik.splitlines():
    if "${" in line:
        start = line.find("${") + 2
        end = line.find("}", start)
        if end > start:
            traefik_vars.add(line[start:end])

# Combine and check
all_vars = compose_vars | traefik_vars
missing = [v for v in all_vars if v not in env_vars]

print("Variables used in docker-compose.yml and traefik.yml:")
print(sorted(all_vars))
if missing:
    print("\nMissing in .env:", missing)
else:
    print("\nAll variables are present in .env!")
