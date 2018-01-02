from io import StringIO

import xml.etree.ElementTree as ET
import urllib.request

tree = ET.parse(urllib.request.urlopen('https://raw.githubusercontent.com/googlei18n/noto-emoji/master/svg/emoji_u1f46f.svg'))
root = tree.getroot()

parent_map = {c:p for p in tree.iter() for c in p}

count = 0


def find_all(node, names):
  all = []
  for name in names:
    all += [n for n in root.findall('.//{http://www.w3.org/2000/svg}' + name)]
  return all

def find_all_shapes(node):
  return find_all(node, ['path', 'rect', 'circle'])

print('query finds %d nodes' % len(find_all_shapes(root)))

for node in find_all_shapes(root):
  node.set('display', 'none')

print('found %s display = none' % len(root.findall(".//*[@display='none']")))

for node in find_all_shapes(root):
  print(node)
  print(find_all_shapes(node))
  if len(find_all_shapes(node)) == 0:
    node.set('display', 'inherit')

    # now set every parent to yes
    parent = parent_map[node]
    while parent in parent_map:
      parent.set('display', 'inherit')
      parent = parent_map[parent]

    # last thing, serialize new_root
    tree.write('output_%03d.svg' % count)
    count += 1

