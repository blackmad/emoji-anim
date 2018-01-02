#!/usr/bin/python

# "quickly" convert pngs in parallel in low quality
# ~/node_modules/.bin/svg2png-many -i output/ -o output/
# alt
# find *svg -print0 | xargs -0 -I _ convert _ _.png
# animate
#  convert output/*png -loop 0 -coalesce   -duplicate 1,-2-1  anim.gif
# open -a "Google Chrome" anim.gif

import xml.etree.ElementTree as ET
import urllib.request
import os
import os.path
import shutil

output_dir = 'output'
show_grids = false

if os.path.exists(output_dir):
  shutil.rmtree(output_dir)
os.makedirs(output_dir)

tree = ET.parse(urllib.request.urlopen('https://raw.githubusercontent.com/googlei18n/noto-emoji/master/svg/emoji_u1f634.svg'))
root = tree.getroot()

parent_map = {c:p for p in tree.iter() for c in p}

count = 0

def find_all(node, names):
  all = []
  for name in names:
    all += [n for n in node.findall('.//{http://www.w3.org/2000/svg}' + name)]
  return all

def find_all_shapes(node):
  return find_all(node, ['path', 'rect', 'circle', 'ellipse'])

def write_current_tree(tree):
  global count
  tree.write(os.path.join(output_dir, 'output_%03d.svg' % count))
  count += 1

def toggle_id(node, id):
  subnode = node.find(".//*[@id='%s']" % id)
  style = subnode.attrib['style']
  if 'display:none;' in style or subnode.attrib['display'] == 'none':
    subnode.set('display', 'inherit')
    subnode.set('style', style.replace('display:none;', ''))
  else:
    subnode.set('display', 'none')

print('query finds %d nodes' % len(find_all_shapes(root)))

for node in find_all_shapes(root):
  node.set('display', 'none')

print('found %s display = none' % len(root.findall(".//*[@display='none']")))

# so this is cool that there's a Layer_2 and Layer_3 that has the guides for the emoji
if show_grids:
  toggle_id(root, 'Layer_2')
  write_current_tree(tree)
  toggle_id(root, 'Layer_3')
  write_current_tree(tree)

layer_1 = root.find(".//*[@id='Layer_1']")

for node in find_all_shapes(layer_1):
  print(count)
  print(node)
  print(find_all_shapes(node))
  if len(find_all_shapes(node)) == 0:
    print(node.attrib)
    node.set('display', 'inherit')

    # now set every parent to yes
    parent = parent_map[node]
    while parent in parent_map:
      parent.set('display', 'inherit')
      parent = parent_map[parent]

    write_current_tree(tree)

if show_grids:
  toggle_id(root, 'Layer_3')
  write_current_tree(tree)
  toggle_id(root, 'Layer_2')
  write_current_tree(tree)