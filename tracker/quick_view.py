import json
j = json.load(open(r'C:\Users\Jeete\Desktop\Job Finder\tracker\all_jobs.json'))
print(f'Total jobs in database: {len(j)}')
print()
for i, job in enumerate(j[:25], 1):
    role = job['role'][:55] if len(job['role']) > 55 else job['role']
    src = job.get('from', '?')
    co = job['co']
    print(f'  {i:2}. [{src:8}] {role}')
    print(f'       {co}')
