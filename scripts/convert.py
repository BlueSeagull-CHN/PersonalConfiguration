import json
import re

# 读取源文件
with open('source.txt', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 解析数据：跳过注释行（以 # 开头）和空行
entries = []
for line in lines:
    line = line.strip()
    if not line or line.startswith('#'):
        continue
    # 格式：名称|API地址|接口类型|可用率
    parts = line.split('|')
    if len(parts) >= 2:
        name = parts[0].strip()
        api_url = parts[1].strip()
        # 提取域名作为 detail（如 https://360zy.com）
        match = re.match(r'(https?://[^/]+)', api_url)
        detail = match.group(1) if match else api_url
        entries.append({
            'name': name,
            'api': api_url,
            'detail': detail
        })

# 构建目标 JSON 结构
# 注意：原 config.json 中有 cache_time 和 api_site 字段
config = {
    "cache_time": 9200,
    "api_site": {}
}

# 按 api_1, api_2, ... 编号
for idx, entry in enumerate(entries, start=1):
    config['api_site'][f'api_{idx}'] = entry

# 写入目标文件（路径：MoonTV/config.json）
with open('MoonTV/config.json', 'w', encoding='utf-8') as f:
    json.dump(config, f, ensure_ascii=False, indent=2)
