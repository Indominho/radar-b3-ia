import json, pathlib, re

root=pathlib.Path('.')
version=json.loads((root/'VERSION.json').read_text())
html=(root/'index.html').read_text()
version_name=version.get('version','')
assert re.fullmatch(r'v\d+\.\d+\.\d+',version_name)
assert version_name in html
assert (root/'index.html').exists()
assert (root/'data/catalog.json').exists()
assert (root/'data/ranking.json').exists()
cat=json.loads((root/'data/catalog.json').read_text())
rank=json.loads((root/'data/ranking.json').read_text())
assert isinstance(cat.get('items'),list) and len(cat['items'])>=250
assert cat.get('count')==len(cat['items'])
assert len({x.get('ticker') for x in cat['items']})==len(cat['items'])
assert all(re.fullmatch(r'[A-Z0-9]{4,7}',x.get('ticker','')) and not x['ticker'].endswith('F') for x in cat['items'])
assert isinstance(rank.get('items'),list) and len(rank['items'])>=10
assert len({x.get('ticker') for x in rank['items']})==len(rank['items'])
assert 'NaN' not in (root/'data/ranking.json').read_text() and 'Infinity' not in (root/'data/ranking.json').read_text()
assert 'data/ranking.json' in html
print('RELEASE10 PASS',version_name)
