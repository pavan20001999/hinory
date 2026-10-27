import json, re, unicodedata, math, difflib, collections
OLD = json.load(open('old/DIRDOC.json'))['DATA'][0]
OLDT = json.load(open('old/old.json'))['TEMPLES'][0]
W = json.load(open('/mnt/user-data/uploads/Downloads/hinory-data.json'))
MINE = []
for l in open('figures.txt'):
    if not l.strip() or l.startswith('#'): continue
    p = l.rstrip('\n').split('|')
    MINE.append(dict(n=p[0], s=int(p[1]), e=int(p[2]), c=p[3], t=p[4], r=p[5], l=p[6], p=p[7], la=float(p[8]), lo=float(p[9]), w=int(p[10]), a=p[11], k=p[12]))
MYT = []
for l in open('temples.txt'):
    if not l.strip() or l.startswith('#'): continue
    p = l.rstrip('\n').split('|')
    MYT.append(dict(n=p[0], d=p[1], g=p[2], p=p[3], la=float(p[4]), lo=float(p[5]), k=p[6]))

HON = r'\b(sant|saint|swami|swamy|swamigal|sri|shri|shree|sree|guru|maharaj|maharshi|bhagat|bhakta|acharya|acharyar|charya|mahaprabhu|thakur|baba|bapa|ji|devi|ma|mata|goswami|tirtha|teertha|saraswati|sarasvati|giri|paramahansa|nayanar|alvar|alwar|azhwar|of|the|i|ii|iii|a|c)\b'
def norm(s):
    s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode().lower()
    s = re.sub(r'\(.*?\)', ' ', s)
    s = re.sub(r'[^a-z ]', ' ', s)
    s = re.sub(HON, ' ', s)
    s = s.replace('aa', 'a').replace('ee', 'i').replace('oo', 'u').replace('th', 't').replace('dh', 'd').replace('sh', 's').replace('bh', 'b').replace('w', 'v')
    return ' '.join(sorted(s.split()))
def km(a, b):
    R = 6371; t = math.pi / 180
    h = math.sin((b[0]-a[0])*t/2)**2 + math.cos(a[0]*t)*math.cos(b[0]*t)*math.sin((b[1]-a[1])*t/2)**2
    return 2*R*math.asin(math.sqrt(h))

OLDCAT = {'Saints & mystics': 'BH', 'Poets & writers': 'PW', 'Yoga & Nath': 'YO', 'Musicians': 'MU', 'Mathematics & astronomy': 'MA', 'Social reformers': 'RF', 'Ayurveda & medicine': 'AY'}
OLDHIST = {'historical': 'H', 'semi-legendary': 'T', 'legendary': 'L'}
recs = []
def add(r): r['id'] = len(recs); recs.append(r); return r

# 1. old (base)
for d in OLD:
    c = OLDCAT[d['category']]
    blob = (d['tradition'] + ' ' + d['note']).lower()
    if c == 'BH' and re.search(r'philosoph|commentar|vedanta|nyaya|mimamsa|founder of .*math|pontiff|shankaracharya|dvaita|acharya|theolog', blob) and not re.search(r'bhakti|poet|hymn|abhang|vachana|songs', blob):
        c = 'AC'
    s = d['year_start'] if isinstance(d['year_start'], int) else None
    e = d['year_end'] if isinstance(d['year_end'], int) else None
    add(dict(n=d['name'], s=s, e=e, c=c, t=d['tradition'], sect=d['sect'], r=d['state'], l=d['language'], p=d['place'], la=round(float(d['latitude']), 3) if d['latitude'] not in ('',None) else None, lo=round(float(d['longitude']), 3) if d['longitude'] not in ('',None) else None,
             w=1 if d['female'] else 0, a=OLDHIST[d['historicity']], k='', note=d['note'], g=d['geo_confidence'], src='v1'))

idx = collections.defaultdict(list)
for r in recs: idx[norm(r['n'])].append(r)
def find(name, s=None, e=None, k=None):
    if k:
        for r in recs:
            if r.get('k') and r['k'].lower() == k.lower(): return r
    key = norm(name)
    if not key: return None
    for r in idx.get(key, []): return r
    best, br = None, 0
    for kk, rs in idx.items():
        if abs(len(kk) - len(key)) > 6 or not kk: continue
        q = difflib.SequenceMatcher(None, kk, key).ratio()
        if q > br: best, br = rs[0], q
    if best and br >= 0.9:
        if s is None or best['s'] is None or (best['s'] - 120 <= (e if e is not None else s) and s <= (best['e'] or best['s']) + 120):
            return best
    return None

# 2. mine
merged_mine = 0
for m in MINE:
    r = find(m['n'], m['s'], m['e'])
    if r:
        merged_mine += 1
        r['k'] = r['k'] or m['k']
        if r['s'] is None: r['s'], r['e'] = m['s'], m['e']
        if not r['l']: r['l'] = m['l']
        if r['c'] == 'BH' and m['c'] in ('AC', 'SG', 'RF', 'MU', 'MA', 'AY', 'YO'): r['c'] = m['c']
        r['src'] += '+v2'
    else:
        r = add(dict(n=m['n'], s=m['s'], e=m['e'], c=m['c'], t=m['t'], sect='', r=m['r'], l=m['l'], p=m['p'], la=m['la'], lo=m['lo'], w=m['w'], a=m['a'], k=m['k'], note='', g='approx', src='v2'))
        idx[norm(r['n'])].append(r)

# 3. wikidata
merged_wd = 0; qmap = {}
for f in W['figures']:
    r = find(f['n'], f['s'], f['e'], f['k'])
    if r:
        merged_wd += 1
        r['k'] = r['k'] or f['k']; r['q'] = f['q']
        if r['s'] is None and f['s'] is not None: r['s'], r['e'] = f['s'], f['e']
        if not r['l'] and f['l']: r['l'] = f['l']
        r['src'] += '+wd'
    else:
        if f['s'] is None or f['e'] - f['s'] > 130: continue
        t = re.sub(r'^(Women |Indian |Hindu )+', '', f['t']).strip() or 'Hindu'
        r = add(dict(n=f['n'], s=f['s'], e=f['e'], c=f['c'], t=t, sect='', r=f['r'], l=f['l'], p=f['p'], la=f['la'], lo=f['lo'], w=f['w'], a=f['a'], k=f['k'], note='', g='approx', src='wd', q=f['q']))
        idx[norm(r['n'])].append(r)
    qmap[f['q']] = r

# lineage links
links = set()
for f in W['figures']:
    a = qmap.get(f['q'])
    if not a: continue
    for g in f.get('so') or []:
        b = qmap.get(g)
        if b and b is not a: links.add((b['id'], a['id']))
    for g in f.get('st') or []:
        b = qmap.get(g)
        if b and b is not a: links.add((a['id'], b['id']))
# a few well-attested curated guru-disciple links (teacher, student) by name
CUR = [('Nathamuni','Yamunacharya'),('Yamunacharya','Ramanuja'),('Ramanuja','Kurathalvan'),('Kurathalvan','Parasara Bhattar'),('Madhvacharya','Jayatirtha'),('Vyasatirtha','Purandara Dasa'),('Vyasatirtha','Kanaka Dasa'),('Sripadaraja','Vyasatirtha'),
       ('Chaitanya Mahaprabhu','Rupa Goswami'),('Chaitanya Mahaprabhu','Sanatana Goswami'),('Rupa Goswami','Jiva Goswami'),('Vallabhacharya','Vitthalnath'),('Vallabhacharya','Surdas'),('Ramananda','Kabir'),('Ramananda','Ravidas'),('Ravidas','Mirabai'),
       ('Nivruttinath','Dnyaneshwar'),('Ramakrishna','Swami Vivekananda'),('Lahiri Mahasaya','Sri Yukteswar Giri'),('Sri Yukteswar Giri','Paramahansa Yogananda'),('Somananda','Utpaladeva'),('Abhinavagupta','Kshemaraja'),('Chattampi Swamikal','Narayana Guru'),
       ('Sai Baba of Shirdi','Upasni Maharaj'),('Charandas','Sahajo Bai'),('Charandas','Daya Bai'),('Srimanta Sankardev','Madhavdev'),('Bhaktivinoda Thakur','Bhaktisiddhanta Sarasvati'),('Bhaktisiddhanta Sarasvati','Bhaktivedanta Swami Prabhupada'),
       ('Swami Sivananda','Swami Chinmayananda'),('Dadu Dayal','Sundardas'),('Matsyendranath','Gorakhnath'),('Gaudapada','Adi Shankara'),('Vasugupta','Somananda'),('Chandrasekharendra Saraswati','Chandrashekhara Bharati III')]
byname = {}
for r in recs: byname.setdefault(r['n'].lower(), r)
cur_added = 0
for a, b in CUR:
    ra = byname.get(a.lower()) or find(a); rb = byname.get(b.lower()) or find(b)
    if ra and rb and ra is not rb and (ra['id'], rb['id']) not in links:
        if a == 'Chandrasekharendra Saraswati': continue
        links.add((ra['id'], rb['id'])); cur_added += 1

# ---------- temples ----------
WT = W['temples']
temples = []
for t in WT:
    temples.append(dict(n=t['n'], la=t['la'], lo=t['lo'], k=t['k'], w=t['w'], y=t['y'], d=t['d'], h=1 if t['h'] else 0, set='', note='', src='wd'))
def tnorm(s):
    s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode().lower()
    s = re.sub(r'\(.*?\)', ' ', s); s = re.sub(r'[^a-z ]', ' ', s)
    s = re.sub(r'\b(temple|mandir|kovil|koil|devasthanam|swamy|swami|sri|shri|shree|arulmigu|the|of|jyotirlinga|peetham|peeth|matha|math)\b', ' ', s)
    return set(w for w in s.split() if len(w) > 2)
def tmatch(name, la, lo, k=None):
    best, bd = None, 9e9
    for t in temples:
        if k and t['k'] and t['k'].lower() == k.lower(): return t
        d = km((la, lo), (t['la'], t['lo']))
        if d < 3 and d < bd:
            a, b = tnorm(name), tnorm(t['n'])
            if a & b: best, bd = t, d
    return best
mo = 0
for o in OLDT:
    t = tmatch(o['name'], o['lat'], o['lon'])
    if t:
        mo += 1
        if o.get('web'): t['w'] = o['web']
        t['set'] = o['set']; t['note'] = o['note']; t['d'] = t['d'] or o['deity']; t['src'] += '+v1'
    else:
        temples.append(dict(n=o['name'], la=round(o['lat'], 3), lo=round(o['lon'], 3), k='', w=o.get('web', ''), y=None, d=o['deity'], h=0, set=o['set'], note=o['note'], src='v1'))
mm = 0
for m in MYT:
    t = tmatch(m['n'], m['la'], m['lo'], m['k'])
    if t:
        mm += 1; t['k'] = t['k'] or m['k']; t['set'] = t['set'] or m['g']; t['d'] = t['d'] or m['d']
    else:
        temples.append(dict(n=m['n'], la=m['la'], lo=m['lo'], k=m['k'], w='', y=None, d=m['d'], h=0, set=m['g'], note='', src='v2'))
SECTRE = [('Shakta', r'shakti|devi|amman|kali|durga|bhagavati|bhagawati|kamakh|tara\b|mata\b|ambika|amba\b|ambaji|chamund|lakshmi|parvati|meenakshi|kamakshi|mookambika|bhavani|bhadrakali|mariamman|sharada|saraswati|gauri|yellamma|santoshi|vaishno|annapurn|tripura'),
 ('Shaiva', r'shiv|siva|śiva|mahadev|jyotirlinga|eswar|ishwar|iswar|esvar|isvar|nath\b|natha\b|linga|nataraj|bhairav|someshwar|rudra|shankar|mahakal|sundareswar|nathar\b'),
 ('Vaishnava', r'vishnu|krishna|rama\b|ram\b|perumal|narayan|venkates|balaji|jagannath|vitthal|vithoba|ranganath|narasimha|varaha|divya desam|govind|gopal|hanuman|anjaney|maruti|keshav|madhav|vasudev|srinivas|padmanabh|guruvayur|badri|dwarka|shrinath|radha|swaminarayan|ranchhod'),
 ('Ganapatya', r'ganesh|ganapati|vinayak|pillaiyar|siddhivinayak|ganpati'),
 ('Kaumara', r'murugan|subramany|kartik|skanda|kumaraswam|dandayuthapani|dhandayuthapani'),
 ('Saura', r'surya|sun temple'),
 ('Ayyappa', r'ayyappa|sastha|shasta')]
def tsect(t):
    for src in (t['d'], t['n'] + ' ' + t['set']):
        s = (src or '').lower(); best = None
        for name, rx in SECTRE:
            m = re.search(rx, s)
            if m and (best is None or m.start() < best[0]): best = (m.start(), name)
        if best: return best[1]
    return 'Other'
for t in temples: t['sc'] = tsect(t)
# drop generic/non-official web domains
for t in temples:
    if t['w'] and re.search(r'web\.archive\.org|wikipedia|wikimapia|facebook|instagram|twitter|youtube|blogspot|wordpress\.com|tripadvisor|templepurohit|templefolks|hindutemples-india|temple-mandir\.in', t['w'], re.I): t['w'] = ''
json.dump(dict(F=recs, T=temples, LINKS=sorted(links)), open('merged.json', 'w'))
print('figures', len(recs), 'from v1', len(OLD), 'mine merged', merged_mine, 'wd merged', merged_wd, 'links', len(links), 'curated added', cur_added)
print('temples', len(temples), 'old matched', mo, 'mine matched', mm, 'with web', sum(1 for t in temples if t['w']))
print(collections.Counter(r['c'] for r in recs)); print(collections.Counter(t['sc'] for t in temples))
print('undated', sum(1 for r in recs if r['s'] is None), 'women', sum(r['w'] for r in recs))

# ---------- clean wikidata-only additions ----------
DROP_T = {"Arya Samajis","religious writers","astrophysicists","Hindi-language","Kerala Sunni-Shafi'i scholars","Ravidassia","astrological writers","cosmologists","Bhajan singers","revivalist writers"}
KEEP_REV = {"Gagangiri Maharaj","Mahanambrata Brahmachari","Anukulchandra Chakravarty","Pandurang Shastri Athavale","Vishnubawa Brahmachari","Hariharananda Giri"}
DROP_N = {"Raj Kapoor","Bakht Singh","O. Rajagopal","Chanakya","Pathani Samanta","Ranjan Roy Daniel","Sita Ram Goel","Mahatma Gandhi","Bal Gangadhar Tilak","N. G. Chandavarkar","Dada Bhagwan","Keladi Chennamma","Kittur Chennamma","B. D. Jatti","S. Nijalingappa","D. C. Pavate","Phakirappa Gurubasappa Halakatti","C. Rajagopalachari","Kuda Bux","Dattatreya","Raja Ram Mohan Roy","Madan Mohan Malaviya","Kanshi Ram","Jagjit Singh","Atal Bihari Vajpayee"}
keep = []
for r in recs:
    if r['src'] == 'wd':
        if r['n'] in DROP_N or r['t'] in DROP_T: continue
        if r['t'] == 'revivalists' and r['n'] not in KEEP_REV: continue
        if r['t'] == 'reformers' and r['n'] not in {"Govindgiri","Odhavram","R. G. Bhandarkar"}: continue
        if r['t'] == 'Lingayatism' and r['n'] not in {"Puttaraj Gawai","Shivakumara Swami"}: continue
        if r['n'] == 'Raghunatha Shiromani': r['c'] = 'AC'; r['t'] = 'Navya-Nyaya'
        if r['t'] in ('revivalists','reformers'): r['c'] = 'RF' if r['c'] not in ('YO','AC') else r['c']
        r['t'] = {'Hindu':'','yogis':'Yoga','yoga teachers':'Modern yoga','spiritual teachers':'','female':'','women':'','mystics':''}.get(r['t'], r['t'])
        r['t'] = re.sub(r'^\d+(st|nd|rd|th)-century (Indian |Hindu )?', '', r['t'])
        r['t'] = r['t'].replace('Monks of the ','').replace('Scientists of the ','').replace(' religious figures','')
        if r['t'] in ('mathematicians','Indian mathematicians'): r['t'] = 'Jyotisha'
    keep.append(r)
# reindex
old2new = {}
for i, r in enumerate(keep): old2new[r['id']] = i; r['id'] = i
links2 = sorted({(old2new[a], old2new[b]) for a, b in links if a in old2new and b in old2new})
json.dump(dict(F=keep, T=temples, LINKS=links2), open('merged.json', 'w'))
print('after clean', len(keep), 'links', len(links2), collections.Counter(r['c'] for r in keep))
