import requests
import re
import random

# Your API URL
API_URL = "https://headless.tebex.io/api/accounts/10gou-2164e9428612bc2608bce500013b85352d95c2df/categories?includePackages=1"
STORE_URL = "https://tebex.haaasib.xyz"

# 🔻 LOW PRIORITY LIST (These will appear rarely)
LOW_PRIORITY_KEYWORDS = [
    "GRUPPE 6",
    "World Interactions",
    "Plane Heist",
]

def fetch_data():
    try:
        r = requests.get(API_URL)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"Error: {e}")
        return None

def get_weighted_random_packages(all_packages, count=6):
    """
    Picks 6 items, but gives 'Low Priority' items a much smaller chance of being picked.
    """
    if len(all_packages) <= count:
        return all_packages
        
    selected = []
    pool = all_packages.copy()
    
    while len(selected) < count and len(pool) > 0:
        weights = []
        for pkg in pool:
            name = pkg.get('name', '')
            weight = 100 # Standard weight for normal items
            
            # Check if this package is in the low priority list
            for keyword in LOW_PRIORITY_KEYWORDS:
                if keyword.lower() in name.lower():
                    weight = 1 # 20x less likely to be picked
                    break
            
            weights.append(weight)
        
        # Pick one item based on weight
        picked_list = random.choices(pool, weights=weights, k=1)
        picked_item = picked_list[0]
        
        selected.append(picked_item)
        pool.remove(picked_item) # Remove from pool so we don't pick it twice
        
    return selected

def generate_html(data):
    html = '<h2 align="center">🛒 Featured Scripts</h2>\n'
    html += '<div align="center">\n<table>\n'
    
    # 1. Collect all packages
    all_packages = []
    if 'data' in data:
        for category in data['data']:
            if 'packages' in category:
                for pkg in category['packages']:
                    all_packages.append(pkg)

    # 2. USE NEW WEIGHTED SELECTOR
    selected_packages = get_weighted_random_packages(all_packages, 6)

    # 3. Create the Grid
    columns = 3
    for i in range(0, len(selected_packages), columns):
        html += '  <tr>\n'
        batch = selected_packages[i:i+columns]
        
        for pkg in batch:
            p_id = pkg.get('id')
            name = pkg.get('name', 'Unknown Script')
            
            if len(name) > 25:
                name = name[:22] + "..."
                
            price = pkg.get('total_price', '0.00')
            currency = pkg.get('currency', 'USD')
            image = pkg.get('image')
            
            if not image:
                image = "https://via.placeholder.com/250x150?text=No+Image"
            
            link = f"{STORE_URL}/package/{p_id}"
            
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

    # Improved Regex to prevent duplication
    pattern = r'()(.*?)()'
    
    # Check if tags exist first
    if not re.search(pattern, content, flags=re.DOTALL):
        print("❌ Error: Could not find SHOP_START/END tags in readme.md")
        return

    replacement = f'\\1\n{new_content}\n\\3'
    
    # This replaces content BETWEEN tags, keeping the tags safe
    new_readme = re.sub(pattern, replacement, content, flags=re.DOTALL, count=1)
    
    with open('readme.md', 'w', encoding='utf-8') as f:
        f.write(new_readme)

if __name__ == "__main__":
    json_data = fetch_data()
    if json_data:
        html_content = generate_html(json_data)
        update_readme(html_content)
        print("✅ README updated. Rare items given low priority.")
