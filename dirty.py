#!/usr/bin/env python

# "quickly" convert pngs in parallel in low quality
# ~/node_modules/.bin/svg2png-many -i output/ -o output/
# alt
# find *svg -print0 | xargs -0 -I _ convert _ _.png
# animate
#  convert output/*png -loop 0 -coalesce +duplicate -duplicate 1,-1-0  anim.gif
# open -a "Google Chrome" anim.gif

import xml.etree.ElementTree as ET
import urllib.request
import os
import os.path
import shutil
import argparse
import emoji

output_dir = 'output'
show_grids = False

if os.path.exists(output_dir):
  shutil.rmtree(output_dir)
os.makedirs(output_dir)

parser = argparse.ArgumentParser()
parser.add_argument("-a", "--animate", action="store_true", default=True)
parser.add_argument("-t", "--twitter", action="store_true", default=True)
parser.add_argument("-g", "--google", action="store_true")
parser.add_argument("codepoint", type=str, help="the emoji codepoint or character or shortname", default="1f634")
args = parser.parse_args()
print(args)

def char_is_emoji(character):
  return character in emoji.UNICODE_EMOJI

codepoint = args.codepoint

print(len(codepoint))
if (char_is_emoji(codepoint)) or len(codepoint) < 4:
  codepoint = '-'.join([str(i.encode("unicode_escape"))[5:-1].lstrip('0') for i in codepoint])

  print(codepoint)

codepoint = codepoint.replace('U+', '').replace('u+', '').lower()
emoji_name = codepoint

if args.google:
  try:
    url = 'https://raw.githubusercontent.com/googlei18n/noto-emoji/master/svg/emoji_u%s.svg' % codepoint
    print(url)
    file = urllib.request.urlopen(url)
  except:
    url = 'https://raw.githubusercontent.com/googlei18n/noto-emoji/master/svg/emoji_u%s_200d_2640.svg' % codepoint
    print(url)
    file = urllib.request.urlopen(url)
elif args.twitter:
  try:
    url = 'https://raw.githubusercontent.com/twitter/twemoji/gh-pages/2/svg/%s.svg' % codepoint
    print(url)
    file = urllib.request.urlopen(url)
  except:
    try:
      url = 'https://raw.githubusercontent.com/twitter/twemoji/gh-pages/2/svg/%s-1f3fe-200d-2640-fe0f.svg' % codepoint
      print(url)
      file = urllib.request.urlopen(url)
    except:
      url = 'https://raw.githubusercontent.com/twitter/twemoji/gh-pages/2/svg/%s.svg' % codepoint.split('-')[0]
      print(url)
      file = urllib.request.urlopen(url)


tree = ET.parse(file)
root = tree.getroot()

parent_map = {c:p for p in tree.iter() for c in p}

count = 0

def find_all(node, names):
  all = []
  for name in names:
    all += [n for n in node.findall('.//{http://www.w3.org/2000/svg}' + name)]

  def has_defs_in_parent(node):
    while node in parent_map:
      node = parent_map[node]
      if 'defs' in node.tag:
        return True
    return False

  all = [a for a in all if not has_defs_in_parent(a)]

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

layer_1 = root
if args.google:
  layer_1 = root.find(".//*[@id='Layer_1']")
  if not layer_1:
    layer_1 = root.find(".//*[@id='图层_1']")

write_current_tree(tree)

for node in find_all_shapes(layer_1):
  if len(find_all_shapes(node)) == 0:
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

if args.animate:
  print('rendering to png')
  # os.system('find output/*svg -print0 | xargs -0 -I _ convert -size 256x256 _ _.png')
  #os.system('find output/*svg -print0 | xargs -0 -I _ svgexport _ _.png 256:256')
  os.system('~/node_modules/.bin/svg2png-many -w 256 -h 256 -i output/ -o output/')
  print('anim')
  os.system('convert -dispose previous output/*png -loop 0 -duplicate 5,-1 -duplicate 1,-1-0 output/output_000.png -duplicate 5,0 output/%s.gif' % emoji_name)
  os.system('open -a "Google Chrome" output/%s.gif' % emoji_name)
