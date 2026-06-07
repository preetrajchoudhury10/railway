import subprocess, json, re, urllib.parse

result = subprocess.run(["curl", "-s", "-A", "Mozilla/5.0", "-L", 
    "https://www.google.com/search?q=generative+AI+fresher+India+2026&hl=en"],
    capture_output=True, text=True, timeout=30)
html = result.stdout
links = re.findall(r'href="(https?://[^"]*)"', html)
job_links = [l for l in links if any(s in l for s in ['linkedin','naukri','internshala','indeed','hirist'])]
for l in job_links[:20]:
    print(urllib.parse.unquote(l))
print(f"\nTotal links found: {len(links)}, job links: {len(job_links)}")
