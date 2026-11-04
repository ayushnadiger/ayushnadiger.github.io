#!/usr/bin/env python3
"""Build the two active project pages' vector figures from retained inputs.

The network and time-line diagrams are explanatory schematics. The routing
bars use the exact testbed values in RESULTS_AND_CODE_DESIGN.md (2 Nov 2026).
The scheduling bars use the fresh matched cohort from async revision 9.
Requires matplotlib and numpy; no simulation is rerun by this script.
"""
from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT/'tools/research_data'
OUT = ROOT/'assets/research'
INK, MUTED, TEAL, RUST, GREY = '#262624', '#686861', '#287276', '#ab6244', '#b3b6b1'
plt.rcParams.update({
    'font.family': 'DejaVu Serif', 'font.size': 13,
    'axes.labelcolor': INK, 'text.color': INK, 'xtick.color': INK,
    'ytick.color': INK, 'axes.edgecolor': '#aaa99f',
    'axes.spines.top': False, 'axes.spines.right': False,
    'svg.fonttype': 'none', 'savefig.facecolor': 'none',
    'axes.facecolor': 'none', 'figure.facecolor': 'none',
})

def save(fig, subdir, name):
    directory = OUT/subdir
    directory.mkdir(parents=True, exist_ok=True)
    fig.savefig(directory/name, format='svg', metadata={'Date': None})
    plt.close(fig)

def shared_junction():
    fig, ax = plt.subplots(figsize=(10, 4.4))
    xy = {'A': (0, 0), '1': (2, 1.2), '2': (1.5, -1.4),
          '3': (3.7, -1.4), '4': (5.3, 0), 'B': (7.5, 0)}
    for a,b,color in [('A','1',INK),('1','4',INK),('A','2',TEAL),
                       ('2','3',TEAL),('3','4',TEAL),('4','B',INK)]:
        ax.add_patch(FancyArrowPatch(xy[a], xy[b], arrowstyle='-|>',
                      mutation_scale=18, shrinkA=22, shrinkB=22,
                      linewidth=2, color=color, zorder=1))
    for name,(x,y) in xy.items():
        hybrid = name in ['A','B']
        ax.scatter(x,y,s=1250 if hybrid else 1050,facecolor=TEAL if hybrid else '#fdfdfc',
                   edgecolor=TEAL if hybrid else INK,linewidth=1.6,zorder=2)
        ax.text(x,y,name,ha='center',va='center',color='white' if hybrid else INK,
                fontsize=16,fontweight='bold',zorder=3)
    ax.text(2.8,1.8,'3-hop route',ha='center',fontsize=14)
    ax.text(2.7,-2.05,'4-hop detour',ha='center',fontsize=14,color=TEAL)
    ax.annotate('Shared junction\nand final link',xy=(6.25,0),xytext=(6.25,1.18),
                ha='center',va='center',fontsize=13,color=MUTED,
                arrowprops={'arrowstyle':'-','color':MUTED,'lw':1})
    ax.text(0,-2.58,'Filled: hybrid endpoints · Open: Type-1 repeaters',
            fontsize=12,color=MUTED)
    ax.set(xlim=(-.65,8.2),ylim=(-2.85,2.1),aspect='equal')
    ax.axis('off')
    fig.subplots_adjust(left=.04,right=.99,top=.98,bottom=.04)
    save(fig,'hybrid','shared-junction.svg')

def routing_bars():
    data=json.loads((DATA/'hybrid-routing.json').read_text())
    names=['Unencoded pair','Three-rail phase REP3']
    values=[data['with_detour'][k]/data['shortest'][k] for k in ['unencoded','phase_rep3']]
    fig,ax=plt.subplots(figsize=(10,6))
    ax.bar([0,1],values,width=.55,color=[GREY,TEAL],zorder=3)
    ax.axhline(1,color=MUTED,linestyle='--',linewidth=1.2,zorder=4)
    for i,value in enumerate(values):
        ax.text(i,value+.07,f'{value:.3f}×',ha='center',fontsize=17,fontweight='bold')
    ax.text(1.45,1.03,'Equal performance',ha='right',fontsize=11,color=MUTED)
    ax.set(xticks=[0,1],xticklabels=names,ylim=(0,2.65),xlim=(-.6,1.6),
           ylabel='Detour / shortest-only objective')
    ax.set_yticks(np.arange(0,2.6,.5))
    ax.grid(axis='y',color='#e4e4de',linewidth=.7,zorder=0)
    ax.tick_params(axis='x',length=0,pad=12)
    fig.subplots_adjust(left=.14,right=.97,top=.94,bottom=.16)
    save(fig,'hybrid','code-route-reversal.svg')

def hidden_window():
    fig,ax=plt.subplots(figsize=(10,5.8))
    ax.axvspan(3,8,color=TEAL,alpha=.075,zorder=0)
    rows=[('Pair a',3,1),('Pair b',2,3),('Pair c',1,7)]
    for label,y,arrival in rows:
        ax.plot([0,9],[y,y],color='#deded6',lw=1,zorder=1)
        ax.plot([arrival,9],[y,y],color=INK,lw=1.8,zorder=2)
        ax.scatter([arrival],[y],s=75,color=INK,zorder=4)
        ax.text(-.35,y,label,ha='right',va='center',fontsize=14)
    for time,ys,label,color in [(4,[2,3],r'$X_aX_b$',RUST),(8,[1,2],r'$X_bX_c$',TEAL)]:
        ax.plot([time,time],[min(ys),max(ys)],color=color,lw=2,zorder=4)
        ax.scatter([time]*len(ys),ys,marker='s',s=105,color=color,zorder=5)
        ax.text(time,max(ys)+.36,label,ha='center',color=color,fontsize=16)
    ax.annotate('',xy=(3,.4),xytext=(8,.4),
                arrowprops={'arrowstyle':'|-|','color':TEAL,'lw':1.5})
    ax.text(5.5,.05,'Hidden-pair window',ha='center',va='top',fontsize=14,color=TEAL)
    ax.text(4,3.92,'First shared check',ha='center',fontsize=12,color=MUTED)
    ax.text(8,3.92,'First separating\ncheck',ha='center',fontsize=12,color=MUTED)
    ax.text(.1,4.2,'Schematic schedule',fontsize=12,color=MUTED,fontstyle='italic')
    ax.set(xlim=(0,9.4),ylim=(-.3,4.5),xticks=np.arange(0,10),yticks=[],xlabel='Time (illustrative units)')
    for side in ['left','right','top']: ax.spines[side].set_visible(False)
    ax.tick_params(axis='x',length=3,pad=7)
    fig.subplots_adjust(left=.14,right=.96,top=.95,bottom=.16)
    save(fig,'async','hidden-window.svg')

def async_bars():
    data=json.loads((DATA/'async-scheduling.json').read_text())['policies']
    policies=['index','greedy','zgreedy','balanced']
    fig,ax=plt.subplots(figsize=(10,6.5))
    x=np.arange(4)
    for key,offset,color,label in [('record_local',-.18,TEAL,'Full local record'),
                                   ('early_standard',.18,GREY,'Early noise only')]:
        rows=[data[p][key] for p in policies]
        y=100*np.array([r['mean'] for r in rows])
        error=100*np.array([[r['mean']-r['lo'] for r in rows],
                            [r['hi']-r['mean'] for r in rows]])
        bars=ax.bar(x+offset,y,width=.33,color=color,label=label,yerr=error,
                    capsize=3,zorder=3,error_kw={'elinewidth':1.1,'ecolor':INK})
        for bar,value,err in zip(bars,y,error[1]):
            ax.text(bar.get_x()+bar.get_width()/2,value+err+1.3,f'{value:.1f}',
                    ha='center',va='bottom',fontsize=11.5)
    ax.set(xticks=x,xticklabels=['Index','X-greedy','Z-greedy','Balanced'],
           ylim=(0,86),ylabel='Twelve-pair block error (%)')
    ax.set_yticks(np.arange(0,81,20))
    ax.grid(axis='y',color='#e4e4de',linewidth=.7,zorder=0)
    ax.tick_params(axis='x',length=0,pad=10)
    ax.legend(frameon=False,loc='upper right',fontsize=12)
    fig.subplots_adjust(left=.12,right=.98,top=.96,bottom=.14)
    save(fig,'async','bb72-scheduling.svg')

if __name__=='__main__':
    shared_junction()
    routing_bars()
    hidden_window()
    async_bars()
    print('Built four research figures from the retained exact/simulation inputs.')
