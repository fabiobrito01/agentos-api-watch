import argparse,time,urllib.request,json
def check(url,timeout=10):
 start=time.perf_counter()
 try:
  with urllib.request.urlopen(url,timeout=timeout) as r: code=r.status
  return {"url":url,"ok":200<=code<400,"status":code,"ms":round((time.perf_counter()-start)*1000)}
 except Exception as e:return {"url":url,"ok":False,"error":str(e),"ms":round((time.perf_counter()-start)*1000)}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('urls',nargs='+');p.add_argument('--json',action='store_true');a=p.parse_args();rows=[check(x) for x in a.urls];print(json.dumps(rows,indent=2) if a.json else '\n'.join(f"{'UP' if r['ok'] else 'DOWN'} {r['url']} {r['ms']}ms" for r in rows));raise SystemExit(not all(r['ok'] for r in rows))
