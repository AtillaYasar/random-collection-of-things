

def text_append(path, appendage):
    with open(path, 'a', encoding='utf-8') as f:
        f.write(appendage)

def text_create(path, content=''):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

def text_read(fileName):
    with open(fileName, 'r', encoding='utf-8') as f:
        contents = f.read()
    return contents

def is_empty(string):
    for char in string:
        if char not in [' ','\t','\n']:
            return False
    return True

# basically writes <element_name, attribute="value", att2="value2"> stuff here </element_name>, but plus recursion:
#   so d['content'] can contain another d, or even a list of d. will keep track of indentation levels.
def write_html(d, ind_level=0):
    ind = ' '*2
    
    if 'attributes' not in d:
        d['attributes'] = {}
        
    if 'content' in d:
        if type(d['content']) == dict:
            content = write_html(d['content'], ind_level)
        elif type(d['content']) == str:
            content = d['content']
        elif type(d['content']) == list:
            content = '\n\n'.join(map(write_html,d['content'],[ind_level]*len(d)))  #i cant believe this actually works lmao
    else:
        content = ''
    
    el = d['element']
    if d['attributes'] == {}:
        opening_tag = f'<{el}>'
    else:
        att = ' '.join([f'{a}="{v}"' for a,v in d['attributes'].items()])
        opening_tag = '<' + ' '.join([el, att]) + '>'
    closing_tag = f'</{el}>'

    middle = '\n'.join([ind*(ind_level+1) + line for line in content.split('\n')])
    if is_empty(middle):
        return '\n'.join([ind*ind_level + opening_tag + closing_tag])
    else:
        return '\n'.join([ind*ind_level + opening_tag,
                          middle,
                          ind*ind_level + closing_tag])

def write_css(classes):
    ind = ' '*2
    lines = []

    for d in classes:
        lines.append(d['tag'] + ' {')
        for k,v in d['attributes'].items():
            lines.append(f'{ind}{k}: {v};')
        lines.append('}')
        lines.append('')
    return '\n'.join(lines)

# example usage below.

pagename = 'lets_all_stop_writing_html_and_css'

css = [
    {'tag':'body',
     'attributes':{
         'font-family': 'Times',
         'font-size': '22px',
         'background-color': 'black',
         'color': 'grey',
         'white-space': 'pre-wrap',
         'width': '50%',
         'margin-top': '20px',
         'margin-left': '20%'
         }
     },
    {'tag':'skdnfjkdsnfskjnf',
     'attributes':{
         'these': '5px',
         'are-totally-real': '69%',
         'attributes': 'fr'
         }
     }
    ]

p1 = {'element':'p',
     'content':'line1'
     }
p2 = {'element':'p',
     'content':'line2'
     }
link = {'element':'link',
        'attributes':{
            'rel':'stylesheet',
            'href':pagename
            }
        }
head = {'element':'head',
        'content':link
        }
body = {'element':'body',
        'content':[head,p1,p2]}
html = {'element':'html',
        'content':body}

text_create(f'{pagename}.html',write_html(html))
text_create(f'{pagename}.css',write_css(css))







