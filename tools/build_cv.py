"""Build the public academic CV: python tools/build_cv.py."""
from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, KeepTogether

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / 'assets' / 'Ayush_Nadiger_CV.pdf'
OUTPUT.parent.mkdir(exist_ok=True)
fonts = Path('/usr/share/fonts/truetype/dejavu')
pdfmetrics.registerFont(TTFont('CVSerif', str(fonts / 'DejaVuSerif.ttf')))
pdfmetrics.registerFont(TTFont('CVSerifBold', str(fonts / 'DejaVuSerif-Bold.ttf')))
pdfmetrics.registerFontFamily('CVSerif', normal='CVSerif', bold='CVSerifBold', italic='CVSerif', boldItalic='CVSerifBold')
styles = {
    'name': ParagraphStyle('name', fontName='CVSerifBold', fontSize=23, leading=28, alignment=TA_CENTER, spaceAfter=7),
    'contact': ParagraphStyle('contact', fontName='CVSerif', fontSize=9.3, leading=13, alignment=TA_CENTER, spaceAfter=6),
    'section': ParagraphStyle('section', fontName='CVSerifBold', fontSize=12.2, leading=16, spaceBefore=15, spaceAfter=7, keepWithNext=True),
    'item': ParagraphStyle('item', fontName='CVSerif', fontSize=10, leading=14, spaceAfter=9),
    'small': ParagraphStyle('small', fontName='CVSerif', fontSize=9.5, leading=13.5, spaceAfter=8),
}
story = []
def p(text, style='item'):
    return Paragraph(text, styles[style])
def add(text, style='item'):
    story.append(p(text, style))
def section(title):
    add(title, 'section')
def entry(title, text):
    story.append(KeepTogether([p('<b>'+title+'</b>'), p(text)]))
def link(url, label):
    return f'<link href="{url}"><u>{label}</u></link>'

add('Ayush Nadiger', 'name')
add('Electrical and Computer Engineering · University of Massachusetts Amherst', 'contact')
add(link('mailto:anadiger@umass.edu','anadiger@umass.edu')+' · '+link('https://ayushnadiger.github.io/','Research website')+' · '+link('https://github.com/ayushnadiger','GitHub')+' · '+link('https://scholar.google.com/citations?user=pOxwKVIAAAAJ&amp;hl=en','Scholar'), 'contact')

section('Education')
add('<b>University of Massachusetts Amherst</b><br/>M.S., Electrical and Computer Engineering, 2026-present.<br/>Thesis committee chair: Don Towsley.')
add('<b>University of Massachusetts Amherst</b><br/>B.S. Honors, Electrical and Computer Engineering; B.S., Mathematics; B.S., Statistics and Data Science, May 2026.<br/>GPA: 3.85. Minors: Engineering Management and Astronomy. Tau Beta Pi.')

section('Research experience')
entry('Graduate Research Assistant, UMass Amherst | August 2026-present',
      'Work with Filip Rozpędek (UMass Amherst, QuaIL) and Stav Haldar (UT Arlington) on hybrid quantum repeater architectures. Member of Don Towsley\'s ACQuIRE lab. Reproduced the supplied chain benchmark and developed hardware-dependent spacing estimates connecting memory coherence, gate errors, and network performance. Two-dimensional routing and placement extensions are under validation.')
entry('Asynchronous quantum error correction | Ongoing',
      'Derived a local-syndrome rank formula and a rate-distance bound for partially executed CSS transversal CNOTs. Established arbitrary-order deferred recovery under coordinate-confined Pauli faults. Built exact stabilizer and Pauli-frame tests, including counterexamples to composing individually recoverable pauses into a safe schedule. Noisy circuit validation and matched-resource performance comparisons remain ongoing.')
entry('Trapped-ion electric-field noise and geometry | 2025-2026',
      'Honors thesis with Christopher Cox and Robert Niffenegger. Derived Green-function geometry factors, enclosure laws, and spatial correlations for trapped-ion electric-field noise; developed numerical geometry diagnostics and connections to billiard return spectra. Public preprint with code and numerical data.')

section('Research presentation')
add('A. Nadiger. <i>Billiard-Theoretic Geometry Diagnostics for Patch-Induced Heating in Trapped-Ions.</i> Massachusetts Undergraduate Research Conference, UMass Amherst, 2026. '+link('https://honorspaths.honors.umass.edu/massurc/home/abstract/4634','Conference abstract')+'.', 'small')

story.append(PageBreak())
section('Public preprints')
add('1. <b>A. Nadiger.</b> <i>Geometry-controlled correlated electric-field noise in enclosed ion traps from billiard return spectra.</i> 2026. '+link('https://arxiv.org/abs/2608.24770','arXiv:2608.24770')+' · '+link('https://github.com/ayushnadiger/noise_recycling','Code and data')+'.', 'small')
add('2. <b>A. Nadiger</b>, A. Caraeni, and K. Schouten. <i>Potential Energy Savings from Quantum Computing-Based Route Optimization.</i> 2026. '+link('https://arxiv.org/abs/2604.16718','arXiv:2604.16718')+'.', 'small')
add('3. <b>A. Nadiger.</b> <i>Randomized-Accelerated FEAST: A Hybrid Approach for Large-Scale Eigenvalue Problems.</i> 2025. '+link('https://arxiv.org/abs/2512.01257','arXiv:2512.01257')+'.', 'small')

section('Manuscripts in preparation')
add('<b>Syndrome Width: A Rate-Distance Barrier for Asynchronously Assembled Transversal Quantum Gates.</b> Exact syndrome-locality formula and ordering-independent bounds for CSS codes.', 'small')
add('<b>Repair Identifiability and Product-Measurement Complexity of Bond Failures in Graph States.</b> Pauli repair witnesses and finite-graph verification. '+link('https://github.com/ayushnadiger/repair-identifiability','Verification code')+'.', 'small')
add('<b>Predictive Rank as a Memory Witness for Quantum Error-Correction Syndrome Records.</b> Circuit/noise separator bounds, finite-sample tests, and conditional checks on public surface-code records.', 'small')
add('<b>Covariance Geometry of Linearized Quantum Erasure Correction.</b> Covariance normal form for linearized Knill-Laflamme constraints and exact rigidity calculations. '+link('https://ayushnadiger.github.io/projects/covariance-geometry-qec.html','Results and verification')+'.', 'small')

section('Earlier experience')
entry('Quantitative Research, Running Point Capital Advisors | Fall 2025',
      'Built a collateralized fund obligation model for private-credit, private-equity, and real-estate cash flows, with tranche waterfalls and Monte Carlo sensitivity analysis. Delivered a technical report and Excel screening model to the CIO.')

section('Technical skills')
add('<b>Research:</b> quantum error correction, stabilizer and CSS codes, quantum networks, graph-state fault diagnosis, numerical linear algebra, Monte Carlo simulation.<br/><b>Programming:</b> Python, NumPy, SciPy, pandas, Matplotlib, C/C++, Rust, Bash, Git, LaTeX, SLURM/HPC.', 'small')

def footer(canvas, doc):
    canvas.saveState()
    canvas.setFont('CVSerif', 8)
    canvas.setFillColor(colors.HexColor('#666666'))
    canvas.drawString(54, 30, 'Ayush Nadiger · Curriculum Vitae')
    canvas.drawRightString(letter[0]-54, 30, str(doc.page))
    canvas.restoreState()

doc = SimpleDocTemplate(str(OUTPUT), pagesize=letter, rightMargin=54, leftMargin=54, topMargin=43, bottomMargin=48, title='Ayush Nadiger - Curriculum Vitae', author='Ayush Nadiger')
doc.build(story, onFirstPage=footer, onLaterPages=footer)
print(OUTPUT)
