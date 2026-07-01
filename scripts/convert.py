import json
import re

# 读取源文件
with open('source.txt', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 解析数据
entries = []
for line in lines:
    line = line.strip()
    if not line or line.startswith('#'):
        continue
    parts = line.split('|')
    if len(parts) >= 2:
        name = parts[0].strip()
        api_url = parts[1].strip()
        match = re.match(r'(https?://[^/]+)', api_url)
        detail = match.group(1) if match else api_url
        entries.append({
            'name': name,
            'api': api_url,
            'detail': detail
        })

# 构建 JSON
config = {
    "cache_time": 9200,
    "api_site": {}
}

for idx, entry in enumerate(entries, start=1):
    config['api_site'][f'api_{idx}'] = entry

# 输出到 MoonTV/config_Update.json
with open('MoonTV/config_Update.json', 'w', encoding='utf-8') as f:
    json.dump(config, f, ensure_ascii=False, indent=2)
