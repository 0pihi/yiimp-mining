import urllib2,ssl,json,re

# Howto:
# 1. Run ccminer benchmark from command prompt to generate benchfile:
#   ccminer-x64 --benchmark > benchmark.txt
#
# 2. Replace the path to benchfile below (use forward slashes for windows)
#
# 3. run this script from command prompt:
#   python yiimp.py
# 
# NOTE/WARNING: This is meant for informative purposes only.
# Hammering the API will result in you being banned/pissing people off.
# Be a responsible adult and don't abuse the API.

benchfile = 'D:/mine/benchmark.txt' # absolute path to your ccminer benchmark file

hashrate={} # global hashrates
results = {}

def getHashrates():
  hashes = [re.findall(r'(\w+)\s:\s+(\d+\.\d+)\skH',line) for line in open(benchfile)]
  for z in [x for x in hashes if len(x)==1]: #oh ffs.
    for v in z:
      hashrate[v[0]]=float(v[1])

def request(url):
  ctx=ssl.create_default_context()
  ctx.check_hostname = False
  ctx.verify_mode = ssl.CERT_NONE
  opener = urllib2.build_opener(urllib2.HTTPSHandler(context=ctx))
  opener.addheaders = [('User-Agent', 'Mozilla/5.0')]
  try:
    req = opener.open(url).read()
  except :
    return 0
  return req

def getYiimp():
  data = json.loads(request("http://api.yiimp.eu/api/currencies"))
  #data = json.loads(request("http://www.zpool.ca/api/currencies"))
  return data

def getPrice(coin):
  longname={ # long names of coins, for CMC
    "btc":"bitcoin"
  }
  lname = longname.get(coin,"")
  data = json.loads(request("https://api.coinmarketcap.com/v1/ticker/" + lname + "/"))
  return data
  
def sortedList():
  getHashrates()
  yiimp=getYiimp()
  btcprice=float(getPrice("btc")[0]["price_usd"])
  for coin in yiimp:
    algo   = yiimp[coin]["algo"]
    hashrt = hashrate.get(algo,0)
    btcpmh = float(yiimp[coin]["estimate"])/(1000**2) #btc/MH/day
    if algo in ('sha256d', 'sha256t', 'blakecoin','blake','blake2s','decred'): #these are different
      btcpmh = btcpmh/1000 #per GH
    btcpd  = btcpmh * hashrt #btc per day
    results[coin] = { "btcpd": btcpd, "algo": algo, "hashrt": hashrt }

  for coin, value in sorted(results.iteritems(), key=lambda (k,v): (v["btcpd"],k)):
    print "[ %-4s ]: %10.8f btc/day (%5.4f USD/day) [algo: %-10s hashrate: %-9.1f kH/s]" % (coin, value["btcpd"], btcprice * value["btcpd"], value["algo"], value["hashrt"])

sortedList()
