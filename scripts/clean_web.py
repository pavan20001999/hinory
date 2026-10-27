import json,re
BAD=r"hindu-blog|hindumandiryatra|hindustantimes|worldplaces|indiaplacesmap|ixigo|//(www\.)?karnataka\.com|keralatemples\.info|keralawindow|khojnu|lightuptemples|mapsofindia|//murugan\.org|ntb\.gov\.np|orissadiary|sambadenglish|shaivam|templenet|templesofkerala|thedivineindia|timesofindia|touristlink|uttaranchaltourism|visittemples|euttaranchal|findmytemple|goldentriangletour|guwahationline|holidify|holyprasadam|ignca|kerala-tourism|keralabackwater|keralaculture|keralatourism|livehindustan|livehistoryindia|maalaimalar|makemytrip|mathrubhumi|nma\.gov\.in|pilgrimaide|ratopati|southtourism|tezu\.ernet|thekeralatemples|thestatesman|vikatan|archive\.org|archive\.today|indiapl\.com|mandironline|nearmein|nuaodisha|/amp/|bbc\.com|whc\.unesco|dinamalar|kathmandupost|ekantipur|dhaka\.gov\.bd|archaeology\.gov\.bd|//asi\.nic\.in|asivadodaracircle|asiguwahaticircle|rtiodisha|rayagada\.nic|pib\.nic|gochhattisgarh|bhaktapur\.com|chelembrapanchayath|dailyexcelsior|hindustan\.com|hassanonline|radha\.name|scroll\.in|trawell|wkimapia|cosmoview|deccanherald|dinamani|eripuram|hrsarchive|kataragama\.org|ratnagiritourism|uvari\.info|vasthurengan|wbcsoftwarelab|newconsys|srisaradacollege|pakistanhinducouncil|sycd\.gujarat|sabarkanthadp|tourist-place|tourism\.html|tourism\.rajasthan|sabarimalaaccomodation|//(www\.)?ayyappa\.com|iyyappaswami|avaalankarams|rcmysore-portal|giridih\.nic|guntur\.nic|kawardha\.nic|pauri\.nic|sonbhadra\.nic|shimoga\.nic|onlinetdb|indiatimes|wix\.com/vilasagar|page\.tl|vellalore\.in/2013|ddcchitwan|maulakalika|//(www\.)?kanakagiri\.in|karimpuzha\.com|marayikkodu|mudikondan|ravanasamudram|ettampadai|agroha\.com|sunama-jakini|//(www\.)?swaminarayan\.in"
def clean(u):
    u=re.split(r'[|}<\s,]',u)[0]
    u=re.sub(r'\?fbclid=.*','',u)
    if re.search(BAD,u,re.I): return ''
    if not re.match(r'https?://[\w.-]+\.[a-z]{2,}',u,re.I): return ''
    return u
if __name__=='__main__':
    M=json.load(open('merged.json'))
    for t in M['T']: t['w']=clean(t['w']) if t['w'] else ''
    json.dump(M,open('merged.json','w'))
    u=sorted({t['w'] for t in M['T'] if t['w']}); json.dump(u,open('urls.json','w')); print(len(u), sum(1 for t in M['T'] if t['w']))
