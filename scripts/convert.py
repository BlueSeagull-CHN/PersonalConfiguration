import json
import re
import requests
import concurrent.futures
import time

# ---------- 配置 ----------
KEEP_RATIO = 0.67          # 保留最快接口的比例（2/3）
TIMEOUT = 5                # 单个接口超时时间（秒）
THREADS = 10               # 并发线程数
MIN_INTERFACES = 10        # 至少保留 10 个（防止比例太低）
# -------------------------

def test_speed(api_url):
    """测试单个接口的响应速度，返回 (api_url, speed_ms, success)"""
    try:
        start = time.time()
        resp = requests.get(api_url, timeout=TIMEOUT, stream=True)
        resp.iter_content(1024)
        elapsed = (time.time() - start) * 1000
        if resp.status_code == 200:
            return (api_url, elapsed, True)
        else:
            return (api_url, None, False)
    except:
        return (api_url, None, False)

# 读取源文件
with open('source.txt', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 解析所有接口
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
            'detail': detail,
            'speed': None
        })

print(f"📡 解析到 {len(entries)} 个接口，开始测速...")

# 提取所有 API URL 用于测速
api_urls = [e['api'] for e in entries]

# 并发测速
speed_results = {}
with concurrent.futures.ThreadPoolExecutor(max_workers=THREADS) as executor:
    future_to_url = {executor.submit(test_speed, url): url for url in api_urls}
    for future in concurrent.futures.as_completed(future_to_url):
        url, speed, success = future.result()
        if success:
            speed_results[url] = speed
            print(f"  ✅ {url[:50]}... {speed:.0f}ms")
        else:
            speed_results[url] = None
            print(f"  ❌ {url[:50]}... 超时或失败")

# 按速度排序，过滤掉失败的接口
valid_entries = []
for entry in entries:
    speed = speed_results.get(entry['api'])
    if speed is not None:
        entry['speed'] = round(speed, 1)
        valid_entries.append(entry)

# 按速度排序（快的在前）
valid_entries.sort(key=lambda x: x['speed'])

# 计算保留数量（至少 MIN_INTERFACES，且不超过有效总数）
max_interfaces = max(MIN_INTERFACES, int(len(valid_entries) * KEEP_RATIO))
# 如果保留数量大于有效总数，则全部保留
if max_interfaces > len(valid_entries):
    max_interfaces = len(valid_entries)

top_entries = valid_entries[:max_interfaces]

print(f"✅ 测速完成，有效接口：{len(valid_entries)} 个，保留 {len(top_entries)} 个（约 {int(KEEP_RATIO*100)}%）")

# 构建最终 JSON
config = {
    "cache_time": 9200,
    "api_site": {}
}

for idx, entry in enumerate(top_entries, start=1):
    clean_entry = {
        'name': entry['name'],
        'api': entry['api'],
        'detail': entry['detail']
    }
    config['api_site'][f'api_{idx}'] = clean_entry

# 写入目标文件
with open('MoonTV/config_Update.json', 'w', encoding='utf-8') as f:
    json.dump(config, f, ensure_ascii=False, indent=2)

print(f"📝 已写入 MoonTV/config_Update.json，包含 {len(top_entries)} 个接口")
