#!/usr/bin/env python3
"""Build the static project index and manuscript readers from retained TeX sources.

Requires pandoc, pdftocairo, and lxml. Run from any directory.
"""
from pathlib import Path
import html
import json
import re
import shutil
import subprocess
from lxml import etree
from lxml import html as lh

ROOT = Path(__file__).resolve().parents[1]
BASE = 'https://ayushnadiger.github.io/'
SOURCES = ROOT / 'assets' / 'papers'
PROJECTS = [
    dict(slug='hybrid-quantum-repeaters', title='Error Correction and Routing in 2D Hybrid Repeater Networks', date='2026 – Present', context='Graduate research with Filip Rozpędek and Stav Haldar · Poster, CQN site visit, October 2026', summary='Encoded hybrid repeaters, placement, and routing for scalable entanglement generation in two-dimensional quantum networks.', ongoing=True),
    dict(slug='asynchronous-qec', title='Asynchronous Quantum Error Correction', date='2026 – Present', context='Ongoing research · Distributed quantum error correction', course_note='Course context: Quantum Information Systems (CS 648).', summary='Error correction and syndrome information when distributed operations depend on entanglement arriving at different times.', ongoing=True),
    dict(slug='trapped-ion-diagnostics', title='Geometry-Controlled Noise in Trapped-Ion Systems', date='2025 – 2026', context='Undergraduate honors thesis · Submitted to Physical Review A · Supervised by Christopher Cox and Robert Niffenegger', summary='How electrode geometry shapes electric-field noise and spatial correlations in trapped-ion systems.', paper='trapped-ion', paper_title='Geometry-controlled correlated electric-field noise in enclosed ion traps from billiard return spectra', version='Preprint · 2026', links=[('arXiv:2608.24770','https://arxiv.org/abs/2608.24770'),('Code & data','https://github.com/ayushnadiger/noise_recycling')]),
    dict(slug='covariance-geometry-qec', title='Differential Geometry of Quantum Erasure Correction', date='2025', context='Differential Geometry course project · Talk, mathematics graduate student seminar, 2025', summary='The geometry of exact erasure-correcting code subspaces, their perturbations, and information leakage.', paper='erasure-geometry', paper_title='Normal Geometry of Exact Quantum Erasure Codes: Covariance, Leakage, and Infinitesimal Rigidity', version='Manuscript · August 2026', links=[]),
    dict(slug='predictive-rank-qec', title='Statistical Memory Tests for Quantum Error-Correction Records', date='2025 – 2026', context='Applied Multivariate Statistics course project · Public Google surface-code data', summary='Predictive-rank tests for temporal structure in syndrome records, with an application to public Google data.', paper='predictive-rank', paper_title='Predictive Rank as a Circuit-Conditioned Memory Witness for Quantum Error-Correction Syndrome Records', version='Manuscript · revised November 2026', links=[]),
    dict(slug='graph-state-repair-diagnosis', title='The Bond Repair Problem in Graph States', date='2025 – 2026', context='Manuscript · Project for the UMass FTQEC seminar', summary='Distinguishing a missing entangling gate from endpoint-memory dephasing using product measurements.', paper='bond-repair', paper_title='The bond repair problem: distinguishing a missing entangling gate from endpoint dephasing in graph states', version='Manuscript · August 2026', links=[('Verification code','https://github.com/ayushnadiger/repair-identifiability')]),
]

PROJECT_PRIORITY = [
    'hybrid-quantum-repeaters', 'asynchronous-qec',
    'graph-state-repair-diagnosis', 'trapped-ion-diagnostics',
    'predictive-rank-qec', 'covariance-geometry-qec',
]
PROJECTS.sort(key=lambda project: PROJECT_PRIORITY.index(project['slug']))

# Author-controlled HTML for brief course and thesis context on the homepage.
HOME_CONTEXT = {
    'hybrid-quantum-repeaters': 'This is graduate research with Filip Rozpędek and Stav Haldar, presented as a poster at the <strong>CQN site visit</strong> (October 2026).',
    'asynchronous-qec': '',
    'trapped-ion-diagnostics': 'This was my <strong>Undergraduate Honors Thesis</strong>. Submitted to <strong>Physical Review A</strong>. <a href="https://arxiv.org/abs/2608.24770">arXiv preprint</a>.',
    'covariance-geometry-qec': 'A <strong>Differential Geometry</strong> course project.',
    'predictive-rank-qec': 'An <strong>Applied Multivariate Statistics</strong> course project.',
    'graph-state-repair-diagnosis': 'Manuscript. <a href="https://github.com/ayushnadiger/repair-identifiability">Code</a>.',
}

def esc(s):
    return html.escape(s, quote=True)

def pandoc(text, extra=()):
    p = subprocess.run(['pandoc','-f','latex','-t','html5','--mathjax','--shift-heading-level-by=1',*extra], input=text, text=True, capture_output=True, check=True)
    if p.stderr.strip():
        print(p.stderr.strip())
    return p.stdout

def group(s, pos):
    """Read a balanced TeX brace group."""
    assert s[pos] == '{'
    depth = 1
    i = pos + 1
    while depth:
        if s[i] == '\\':
            i += 2
            continue
        depth += (s[i] == '{') - (s[i] == '}')
        i += 1
    return s[pos+1:i-1], i

def raw_html(markup):
    return '\n\\begin{rawhtml}\n'+markup+'\n\\end{rawhtml}\n'

def read_paper(project):
    directory = SOURCES / project['paper']
    tex = (directory/'main.tex').read_text()
    # Comments are non-rendering TeX; preserve escaped percent signs.
    tex = re.sub(r'(?<!\\)%[^\n]*', '', tex)
    abstract = re.search(r'\\begin\{abstract\}(.*?)\\end\{abstract\}',tex,re.S).group(1)
    start = tex.index('\\end{abstract}') + len('\\end{abstract}')
    body = tex[start:tex.index('\\end{document}')]
    preamble = tex[:tex.index('\\begin{document}')]
    # Only macros are needed from the preamble; title/author/package commands
    # are supplied by the semantic HTML wrapper rather than copied as UI.
    macros = []
    for m in re.finditer(r'\\(?:newcommand|renewcommand|DeclareMathOperator)\*?',preamble):
        j=m.end()
        while j<len(preamble) and preamble[j].isspace(): j+=1
        if preamble[j]!='{': continue
        _,j=group(preamble,j)
        while j<len(preamble) and (preamble[j].isspace() or preamble[j]=='['):
            if preamble[j]=='[': j=preamble.index(']',j)+1
            else: j+=1
        if preamble[j]=='{':
            _,j=group(preamble,j)
            macros.append(preamble[m.start():j])
    prefix='\n'.join(macros)+'\n'+r'\newcommand{\bm}[1]{\boldsymbol{#1}}'+'\n'

    # Build the bibliography without losing citation labels in Pandoc's
    # generic treatment of thebibliography.
    refs = []
    bib = re.search(r'\\begin\{thebibliography\}\{[^}]*\}(.*?)\\end\{thebibliography\}',body,re.S)
    if bib:
        items = re.split(r'\\bibitem(?:\[[^\]]*\])?\{([^}]+)\}',bib.group(1))
        for i in range(1,len(items),2):
            refs.append((items[i],pandoc(prefix+items[i+1].strip())))
        body=body[:bib.start()]+body[bib.end():]
    elif (directory/'references.bib').exists():
        bib_json=json.loads(subprocess.check_output(['pandoc',str(directory/'references.bib'),'-f','biblatex','-t','csljson'],text=True))
        cited=[]
        for m in re.finditer(r'\\(?:cite|citep|citet)(?:\[[^\]]*\])?\{([^}]+)\}',abstract+body):
            for key in m.group(1).split(','):
                if key.strip() not in cited: cited.append(key.strip())
        by_id={x['id']:x for x in bib_json}
        for key in cited:
            entry=by_id[key]
            names=[]
            for a in entry.get('author',[]):
                names.append(a.get('literal') or ' '.join([a.get('given',''),a.get('family','')]).strip())
            year=entry.get('issued',{}).get('date-parts',[['']])[0][0]
            title=entry.get('title','')
            container=entry.get('container-title','')
            url=entry.get('URL') or ('https://doi.org/'+entry['DOI'] if entry.get('DOI') else '')
            text=esc(', '.join(names))+'. <cite>'+title+'</cite>. '+esc(str(container))+(f' ({year}).' if year else '.')
            if url: text+=' <a href="'+esc(url)+'">'+('DOI' if entry.get('DOI') else 'Source')+'</a>'
            refs.append((key,'<p>'+text+'</p>'))
        body=re.sub(r'\\printbibliography(?:\[[^\]]*\])?','',body)
    ref_nums={key:str(i+1) for i,(key,_) in enumerate(refs)}

    # Convert author-supplied TeX figures to browser-native vector images.
    figure_num=0
    figure_labels={}
    def figure(m):
        nonlocal figure_num
        figure_num+=1
        fragment=m.group(0)
        label=re.search(r'\\label\{([^}]+)\}',fragment)
        fid=label.group(1) if label else f'figure-{figure_num}'
        figure_labels[fid]=str(figure_num)
        cap=re.search(r'\\caption(?:\[[^\]]*\])?\{',fragment)
        caption=group(fragment,cap.end()-1)[0] if cap else ''
        pic=re.search(r'\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}',fragment)
        path=pic.group(1) if pic else 'diagram.svg'
        if path.endswith('.pdf'): path=path[:-4]+'.svg'
        elif path.endswith('.png') and (directory/path).with_suffix('.svg').exists(): path=path[:-4]+'.svg'
        # Safe descriptive alternative from the original caption.
        caption_html=pandoc(prefix+caption).strip()
        caption_text=re.sub('<[^>]*>','',caption_html)
        markup=f'<figure id="{esc(fid)}"><img src="../assets/papers/{project["paper"]}/{esc(path)}" alt="Figure {figure_num}; full description in the caption below." loading="lazy"><figcaption><strong>Figure {figure_num}.</strong> '+re.sub(r'^<p>|</p>$','',caption_html)+ '</figcaption></figure>'
        return raw_html(markup)
    body=re.sub(r'\\begin\{figure\*?\}(?:\[[^\]]*\])?.*?\\end\{figure\*?\}',figure,body,flags=re.S)

    # Number sections, theorem environments, and displayed equations before
    # conversion so the paper's internal links stay useful in HTML.
    labels=dict(figure_labels)
    section=0; subsection=0; theorem=0; equation=0; table_num=0; appendix=False
    theorem_by_section='\\newtheorem{theorem}{Theorem}[section]' in preamble
    independent_theorems=project['paper']=='trapped-ion'
    counts={}
    current=''
    token=re.compile(r'\\appendix|\\(?:subsection|section)(?:\*)?\{|\\begin\{table\}|\\begin\{(?:equation|align)\}|\\begin\{(?:theorem|lemma|proposition|corollary|definition|remark|observation|example|conjecture|problem)\}(?:\[[^\]]*\])?|\\label\{([^}]+)\}')
    chunks=[]; last=0
    for m in token.finditer(body):
        if m.start()<last: continue
        chunks.append(body[last:m.start()])
        val=m.group(0)
        if val=='\\appendix':
            appendix=True; section=0; current=''; last=m.end(); continue
        if val.startswith('\\section') or val.startswith('\\subsection'):
            title,end=group(body,m.end()-1)
            starred='*' in val
            is_sub=val.startswith('\\subsection')
            if starred: num=''
            elif is_sub:
                subsection+=1; num=(chr(64+section) if appendix else str(section))+'.'+str(subsection)
            else:
                section+=1; subsection=0
                if theorem_by_section: theorem=0
                num=chr(64+section) if appendix else str(section)
            current=num
            title_prefix=(num+'. ' if not is_sub else num+' ') if num else ''
            chunks.append(('\\subsection' if is_sub else '\\section')+'{'+title_prefix+title+'}')
            last=end
        elif val=='\\begin{table}':
            table_num+=1; current=str(table_num)
            chunks.append(val); last=m.end()
        elif val.startswith('\\begin{equation}') or val.startswith('\\begin{align}'):
            env='align' if 'align' in val else 'equation'
            end=body.index('\\end{'+env+'}',m.end())+len('\\end{'+env+'}')
            content=body[m.end():end-len('\\end{'+env+'}')]
            anchors=[]
            if env=='equation':
                equation+=1; current=str(equation)
                for key in re.findall(r'\\label\{([^}]+)\}',content):
                    labels[key]=current; anchors.append('\\hypertarget{'+key+'}{}')
                content=re.sub(r'\\label\{[^}]+\}','',content)
                content+='\\tag{'+current+'}'
            else:
                rows=re.split(r'(\\\\(?:\[[^\]]*\])?)',content)
                for i in range(0,len(rows),2):
                    row=rows[i]
                    if not row.strip(): continue
                    numbered='\\nonumber' not in row and '\\notag' not in row
                    if numbered:
                        equation+=1; current=str(equation)
                    for key in re.findall(r'\\label\{([^}]+)\}',row):
                        labels[key]=current; anchors.append('\\hypertarget{'+key+'}{}')
                    row=re.sub(r'\\label\{[^}]+\}','',row)
                    if numbered: row+='\\tag{'+current+'}'
                    rows[i]=row
                content=''.join(rows)
            chunks.append('\n'+''.join(anchors)+'\n\\begin{'+env+'*}'+content+'\\end{'+env+'*}\n')
            last=end
        elif val.startswith('\\begin{'):
            env=re.search(r'\{([^}]+)\}',val).group(1)
            if independent_theorems:
                counts[env]=counts.get(env,0)+1; num=str(counts[env])
            else:
                theorem+=1; num=((chr(64+section) if appendix else str(section))+'.' if theorem_by_section else '')+str(theorem)
            current=num
            name=re.search(r'\[([^\]]*)\]$',val)
            heading=env.title()+' '+num+(' ('+name.group(1)+')' if name else '')+'.'
            chunks.append('\\begin{quote}\\textbf{'+heading+'} ')
            last=m.end()
        else:
            key=m.group(1)
            labels[key]=current
            chunks.append('\\hypertarget{'+key+'}{}')
            last=m.end()
    chunks.append(body[last:])
    body=''.join(chunks)
    body=re.sub(r'\\end\{(?:theorem|lemma|proposition|corollary|definition|remark|observation|example|conjecture|problem)\}',r'\\end{quote}',body)
    body=body.replace('\\begin{acknowledgments}','\\section*{Acknowledgments}').replace('\\end{acknowledgments}','')
    body=re.sub(r'\\label\{[^}]+\}','',body)
    def refs_replace(m):
        kind,key=m.group(1),m.group(2)
        values=[]
        for item in key.split(','):
            item=item.strip()
            if item not in labels: raise ValueError('Unresolved reference '+item+' in '+project['paper'])
            label=labels[item]
            if kind=='eqref': label='('+label+')'
            elif kind in ('cref','Cref'):
                prefix={'eq':'Equation','thm':'Theorem','lem':'Lemma','prop':'Proposition','cor':'Corollary','sec':'Section','app':'Appendix','fig':'Figure','tab':'Table','def':'Definition','rem':'Remark'}.get(item.split(':')[0],'Result')
                label=prefix+' '+label
            values.append('\\href{#'+item+'}{'+label+'}')
        return ', '.join(values)
    body=re.sub(r'\\(eqref|ref|cref|Cref)\{([^}]+)\}',refs_replace,body)
    def cite(m):
        values=[]
        for key in m.group(1).split(','):
            key=key.strip()
            if key not in ref_nums: raise ValueError('Missing bibliography entry '+key)
            values.append('\\href{#ref-'+key+'}{'+ref_nums[key]+'}')
        return '['+', '.join(values)+']'
    body=re.sub(r'\\(?:cite|citep|citet)(?:\[[^\]]*\])?\{([^}]+)\}',cite,body)
    # TeX text inside math cannot contain a nested browser link; retain its
    # citation number while the full reference remains linked in the text.
    body=re.sub(r'\\text\{\[\\href\{#ref-[^}]+\}\{(\d+)\}\]\}',lambda m:r'\text{['+m.group(1)+']}',body)
    abstract=re.sub(r'\\(?:cite|citep|citet)(?:\[[^\]]*\])?\{([^}]+)\}',cite,abstract)
    # Pandoc intentionally retains rawhtml; replace those blocks after parsing.
    blocks=[]
    def hold(m):
        blocks.append(m.group(1)); return '\nSITEBLOCK'+str(len(blocks)-1)+'END\n'
    body=re.sub(r'\\begin\{rawhtml\}(.*?)\\end\{rawhtml\}',hold,body,flags=re.S)
    rendered=pandoc(prefix+body)
    for i,markup in enumerate(blocks):
        rendered=rendered.replace('<p>SITEBLOCK'+str(i)+'END</p>',markup)
    abstract_html=pandoc(prefix+abstract)
    refs_html='<section id="references"><h2>References</h2><ol class="paper-references">'+''.join('<li id="ref-'+esc(key)+'">'+content+'</li>' for key,content in refs)+'</ol></section>'
    # The Contents is generated from the rendered headings, including appendices.
    doc=lh.fragment_fromstring('<div>'+rendered+'</div>')
    # Pandoc normalizes align to aligned. Explicit per-row tags require the
    # AMS align environment in MathJax, so restore it where tags occur.
    for span in doc.xpath('.//span[contains(@class,"math")]'):
        if span.text:
            span.text=re.sub(r'\\begin\{aligned\}(.*?)\\end\{aligned\}',lambda m:(r'\begin{align*}'+m.group(1)+r'\end{align*}') if r'\tag' in m.group(1) else m.group(0),span.text,flags=re.S)
    for anchor in doc.xpath('.//a[@data-reference]'):
        key=anchor.get('data-reference')
        if key not in labels: raise ValueError('Unresolved caption reference '+key)
        anchor.text=('('+labels[key]+')') if anchor.get('data-reference-type')=='eqref' else labels[key]
        del anchor.attrib['data-reference']
        del anchor.attrib['data-reference-type']
    for i,caption in enumerate(doc.xpath('.//table/caption'),1):
        caption.text='Table '+str(i)+'. '+(caption.text or '')
    contents=[]
    for i,h in enumerate(doc.xpath('.//h2|.//h3')):
        hid=h.get('id') or 'paper-section-'+str(i+1)
        h.set('id',hid)
        contents.append('<li class="toc-'+h.tag+'"><a href="#'+hid+'">'+esc(' '.join(h.text_content().split()))+'</a></li>')
    rendered=''.join(etree.tostring(x,encoding='unicode',method='html') for x in doc)
    contents.append('<li><a href="#references">References</a></li>')
    return abstract_html,rendered+refs_html,'<ol>'+''.join(contents)+'</ol>'

def page_head(title,description,path,reader=False):
    return f'''<!doctype html>
<html lang="en"><head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(title)} | Ayush Nadiger</title>
  <meta name="description" content="{esc(description)}">
  <link rel="canonical" href="{BASE+path}">
  <link rel="icon" href="/favicon.svg" type="image/svg+xml">
  <link rel="stylesheet" href="{'../' if path.startswith('projects/') else ''}css/style.css">
  {('<link rel="stylesheet" href="../css/paper.css">' + chr(10) + '<script>window.MathJax={loader:{load:["[tex]/html","[tex]/boldsymbol"]},tex:{tags:"none",packages:{"[+]": ["ams","html","boldsymbol"]}},options:{skipHtmlTags:["script","noscript","style","textarea","pre","code"]},chtml:{displayOverflow:"scroll"}};</script>' + chr(10) + '<script defer src="https://cdn.jsdelivr.net/npm/mathjax@3.2.2/es5/tex-chtml.js"></script>') if reader else ''}
</head><body class="project-page{' reader-page' if reader else ''}">
<a class="skip-link" href="#main">Skip to content</a>
'''

def build():
    rows=[]
    for p in PROJECTS:
        summary_html=esc(p['summary'])
        if HOME_CONTEXT[p['slug']]: summary_html+=' '+HOME_CONTEXT[p['slug']]
        rows.append(f'''    <article class="project-entry">
      <h3><a href="projects/{p['slug']}.html">{esc(p['title'])}</a></h3>
      <p class="project-date">{esc(p['date'])}</p>
      <p>{summary_html}</p>
    </article>''')
        path='projects/'+p['slug']+'.html'
        result=page_head(p['title'],p['summary'],path,reader=True)
        result+=f'''<main class="container" id="main">
  <p class="back-link"><a href="../index.html#projects">← Projects</a></p>
  <section class="project-overview" aria-labelledby="project-title">
    <h1 id="project-title">{esc(p['title'])}</h1>
    <p class="project-date">{esc(p['date'])}</p>
    <p class="project-context">{esc(p['context'])}</p>
    <p>{esc(p['summary'])}</p>
  </section>
'''
        if p.get('links'):
            result+='<p class="project-links">'+'<span aria-hidden="true"> · </span>'.join('<a href="'+esc(url)+'">'+esc(label)+'</a>' for label,url in p['links'])+'</p>\n'
        if p.get('ongoing'):
            notice='<aside class="work-in-progress" aria-label="Research status"><p><strong>Ongoing work.</strong> This page summarizes research in progress. Results, methods, and conclusions may change as the work develops.</p></aside>\n'
            result=result.replace('  <section class="project-overview"',notice+'  <section class="project-overview"',1)
            content=(ROOT/'tools'/'project_content'/(p['slug']+'.html')).read_text()
            fragment=lh.fragment_fromstring('<div>'+content+'</div>')
            for figure in fragment.xpath('.//figure'):
                image=figure.find('img')
                link=lh.Element('a',href=image.get('src'),**{'aria-label':'Enlarge figure'})
                figure.replace(image,link)
                link.append(image)
                zoom=lh.Element('a',href=image.get('src'),**{'class':'figure-zoom'})
                zoom.text='Enlarge figure'
                figure.find('figcaption').append(zoom)
            content=''.join(etree.tostring(x,encoding='unicode',method='html') for x in fragment)
            result+='<article class="manuscript project-research" aria-label="Research overview">\n'+content+'\n</article>\n'
            if p.get('course_note'):
                result+='<p class="small muted course-note">'+esc(p['course_note'])+'</p>\n'
        else:
            abstract,body,toc=read_paper(p)
            result+='<aside class="paper-toc" aria-label="Paper contents"><details><summary>Contents</summary>'+toc+'</details></aside>\n'
            result+='<article class="manuscript" id="paper" aria-label="Full paper">\n'
            result+='<section class="manuscript-abstract" id="abstract"><h3>Abstract</h3>'+abstract+'</section>\n'+body+'\n</article>\n'
        result+='</main></body></html>\n'
        (ROOT/path).write_text('\n'.join(line.rstrip() for line in result.splitlines())+'\n')
    index=(ROOT/'index.html').read_text()
    index=re.sub(r'<nav class="site-nav".*?</nav>\s*','',index,flags=re.S)
    index=index.replace('My thesis is chaired by','My thesis is currently chaired by')
    begin=index.index('  <section class="abstract"')
    finish=index.index('  <p class="front-links">',begin)
    about='''  <section class="abstract" aria-label="About">
    <p>I study fault-tolerant quantum computing in distributed systems, focusing on quantum error correction and entanglement generation over noisy links. I am applying to PhD programs for <strong>Fall 2027</strong>.</p>
    <p>I am an ECE master's student at UMass Amherst and a graduate research assistant under
    <a href="https://www.cics.umass.edu/about/directory/filip-rozpedek">Filip Rozpędek</a> in the
    <a href="https://quail.cs.umass.edu/">Quantum Information Lab (QuaIL)</a>.
    My thesis is currently chaired by <a href="https://www.cics.umass.edu/about/directory/don-towsley">Don Towsley</a> in the
    <a href="https://www.cics.umass.edu/organizations/acquire">ACQuIRE lab</a>. I work on hybrid repeaters with
    <a href="https://www.uta.edu/academics/faculty/profile?user=stav.haldar">Stav Haldar</a> at UT Arlington.</p>
  </section>
  <section class="paper-section" id="projects" aria-labelledby="projects-heading">
    <h2 id="projects-heading">Projects</h2>
'''
    talks='''  <section class="paper-section" id="talks" aria-labelledby="talks-heading">
    <h2 id="talks-heading">Talks and Posters</h2>
    <ul class="talk-list">
      <li><a href="projects/hybrid-quantum-repeaters.html"><em>Role of Error Correction in 2D Quantum Networks</em></a>, poster, CQN site visit, October 2026</li>
      <li><a href="projects/trapped-ion-diagnostics.html"><em>Geometry-Controlled Noise in Trapped-Ion Systems</em></a>, poster, Massachusetts Undergraduate Research Conference (MassURC), 2026</li>
      <li><a href="projects/trapped-ion-diagnostics.html"><em>Geometry-Controlled Noise in Trapped-Ion Systems</em></a>, poster, UMass ECE thesis session, 2026</li>
      <li><a href="projects/covariance-geometry-qec.html"><em>Differential Geometry of Quantum Erasure Correction</em></a>, talk, UMass mathematics graduate student seminar, 2025</li>
    </ul>
  </section>
'''
    teaching='''  <section class="paper-section" id="teaching" aria-labelledby="teaching-heading">
    <h2 id="teaching-heading">Teaching</h2>
    <p>Teaching assistant, UMass Amherst ECE:</p>
    <ul class="talk-list">
      <li>ECE 214 Probability and Statistics and ECE 315 Signal Processing Methods, with Prof. Dennis Goeckel</li>
      <li>ECE 201 Analytical Tools for ECE and ECE 213 Continuous-Time Signals and Systems, with Prof. Bill Leonard</li>
      <li>ECE 202 Computational Tools for ECE, with Prof. Marco Duarte</li>
    </ul>
  </section>
'''
    index=index[:begin]+about+'\n'.join(rows)+'\n  </section>\n'+talks+teaching+index[finish:]
    index=index.replace('<main class="container home">','<main class="container home" id="main">')
    if 'class="skip-link"' not in index:
        index=index.replace('<body>','<body>\n<a class="skip-link" href="#main">Skip to content</a>')
    (ROOT/'index.html').write_text(index)
    urls=['']+['projects/'+p['slug']+'.html' for p in PROJECTS]
    (ROOT/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'+''.join('  <url><loc>'+BASE+u+'</loc></url>\n' for u in urls)+'</urlset>\n')
    print('Built homepage and six project pages.')

if __name__=='__main__': build()
