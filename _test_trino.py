import http.client, json, time

body = '{"statement":"SHOW CATALOGS"}'
print('SEND:', body)
conn = http.client.HTTPConnection('localhost', 8080, timeout=10)
conn.request('POST', '/v1/statement', body=body,
             headers={'Content-Type': 'application/json', 'X-Trino-User': 'trino'})
r = conn.getresponse()
print('status:', r.status)
data = r.read().decode()
init = json.loads(data)
print('init state:', init.get('stats', {}).get('state'))
nxt = init.get('nextUri')
print('nextUri:', nxt)

for i in range(20):
    time.sleep(1.5)
    c2 = http.client.HTTPConnection('localhost', 8080, timeout=10)
    c2.request('GET', nxt.replace('http://localhost:8080', ''),
               headers={'X-Trino-User': 'trino'})
    r2 = c2.getresponse()
    obj = json.loads(r2.read().decode())
    st = obj.get('stats', {}).get('state', '?')
    print('poll', i+1, st)
    if st in ('FINISHED', 'FAILED'):
        if 'error' in obj:
            print('ERR:', obj['error'].get('message', '')[:300])
        if 'data' in obj:
            cols = [c['name'] for c in obj.get('columns', [])]
            print('cols:', cols)
            for row in obj['data']:
                print(row)
        break
