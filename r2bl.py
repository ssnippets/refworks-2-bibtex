import re
def read_file(fname):
    rtv = ""
    with open(fname, 'r') as f:
        rtv = f.readlines()
    return [x.strip() for x in rtv]

def process_keys(line, keys):
    if re.match('^[a-zA-Z0-9]+=[a-zA-Z0-9 ]+', line):
        l = line.split('=')
        keys.append(l[0])

def process_str(line):
    return line.replace('%', '\\%')
def process_bib(line, keys, o):
    if re.match('^[a-zA-Z0-9]+ [a-zA-Z0-9 ]+', line):
        l = line.split(' ',1)
        if l[0] in keys:
            o.setdefault(l[0], list()).append(process_str(l[1]))
    return o
def process_refbib(lines):
    mode = 0 #read in the key
    keys = []
    bib = []
    current_item = {}
    for line in lines:
        if line.startswith('BEGIN EXPORTED REFERENCES'):
            #print repr(keys)
            mode += 1 # start processing bibs
        elif line == '':
            if len(current_item.values()) > 0:
                bib.append(current_item)
                current_item = {}
        elif mode == 0:
            process_keys(line, keys)
        elif mode == 1:
            process_bib(line, keys, current_item)
    return bib

def templatize(bib):
    rtv = ""
    t = '''
@%(_type)s {
    %(_id)s,'''
    kt='\n    %s={%s}'
    for i in bib:
        bibobj={}
        # Reference Type:
        rt = i['RT'][0]
        if rt == 'Generic':
            reftype='misc'
        elif rt =='Journal Article':
            reftype='article'
        else: reftype=rt
        bibobj['_type'] = reftype
        
        #make id, and authors:
        authors = i['A1']
        _id = authors[0].split(',')[0].lower()
        bibobj['_id'] = _id
        
        sauthors = " and ".join(authors)
        bibobj['author'] = sauthors
        
        #year:
        bibobj['year'] = i['YR'][0]

        #title:
        bibobj['title'] = i['T1'][0]

        #journal:
        bibobj['journal'] = i.get('JF', False)

        #volume
        bibobj['volume'] = i.get('VO',False)

        #pages:
        if i.get('SP', False):
            pages = i.get('SP')[0]
            if i.get('OP', False):
                pages += '-' + i.get('OP')[0]
            bibobj['pages'] = pages
       
        #abstract:
        bibobj['abstract'] = i.get('AB', False)


        #TODO... ADD MORE AS NEEDED
#        bibobj[''] = i.get('', False)
#        bibobj[''] = i.get('', False)
#        bibobj[''] = i.get('', False)
        rendered = t%bibobj
        rk = []
        for key, val in bibobj.iteritems():
            if key[0] == '_' or not val:
                continue
            elif type(val) == list:
                val = val[0]
            rk.append(kt%(key, val))
        rendered += ','.join(rk) + "\n}"
        rtv += rendered
    print rtv

if __name__ == '__main__':
    from pprint import pprint
    f = read_file('./bib.ref')
    #pprint(f)
    bib = process_refbib(f)
    #pprint(bib)
    templatize(bib)
