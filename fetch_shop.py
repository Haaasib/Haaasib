import requests
import re
import random

API_URL = "https://headless.tebex.io/api/accounts/10gou-2164e9428612bc2608bce500013b85352d95c2df/categories?includePackages=1"
STORE_URL = "https://tebex.haaasib.xyz"

BLOCKED_KEYWORDS = ["GRUPPE 6", "World Interactions", "Hunting Props"]

def fetch_data():
    try:
        r = requests.get(API_URL)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"Error: {e}")
        return None

def get_random_packages(all_packages, count=6):
    allowed_packages = []
    for pkg in all_packages:
        name = pkg.get('name', '')
        is_blocked = False
        for keyword in BLOCKED_KEYWORDS:
            if keyword.lower() in name.lower():
                is_blocked = True
                break
        if not is_blocked:
            allowed_packages.append(pkg)

    if len(allowed_packages) > count:
        return random.sample(allowed_packages, count)
    else:
        return allowed_packages

def generate_html(data):
    html = '<h2 align="center">🛒 Featured Scripts</h2>\n'
    html += '<div align="center">\n<table>\n'
    
    all_packages = []
    if 'data' in data:
        for category in data['data']:
            if 'packages' in category:
                for pkg in category['packages']:
                    all_packages.append(pkg)

    selected_packages = get_random_packages(all_packages, 6)

    columns = 3
    for i in range(0, len(selected_packages), columns):
        html += '  <tr>\n'
        batch = selected_packages[i:i+columns]
        for pkg in batch:
            p_id = pkg.get('id')
            name = pkg.get('name', 'Unknown')
            if len(name) > 25: name = name[:22] + "..."
            price = pkg.get('total_price', '0.00')
            currency = pkg.get('currency', 'USD')
            image = pkg.get('image') or "https://via.placeholder.com/250x150?text=No+Image"
            link = f"{STORE_URL}/product/{p_id}"
            
            html += f'''    <td align="center" width="33%">
      <img src="{image}" width="100%" alt="{name}"><br/>
      <b>{name}</b><br/>
      <code>{price} {currency}</code><br/>
      <a href="{link}">
        <img src="https://img.shields.io/badge/Buy_Now-0051ff?style=for-the-badge&logo=ko-fi&logoColor=white" height="25"/>
      </a>
    </td>\n'''
        html += '  </tr>\n'
    html += '</table>\n</div>'
    return html

def update_readme(new_content):
    with open('readme.md', 'r', encoding='utf-8') as f:
        content = f.read()

    pattern = r'(<!-- SHOP_START -->)(.*?)(<!-- SHOP_END -->)'

    if not re.search(pattern, content, flags=re.DOTALL):
        print("❌ Error: SHOP_START / SHOP_END not found")
        return

    replacement = r'\1\n' + new_content + r'\n\3'

    new_readme = re.sub(
        pattern,
        replacement,
        content,
        flags=re.DOTALL
    )

    with open('readme.md', 'w', encoding='utf-8') as f:
        f.write(new_readme)


if __name__ == "__main__":
    json_data = fetch_data()
    if json_data:
        html_content = generate_html(json_data)
        update_readme(html_content)
        print("✅ README updated.")
