from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

def render(path):
    fig, ax = plt.subplots(figsize=(9.0, 3.5))
    ax.set(xlim=(0, 10), ylim=(0, 4.4))
    ax.axis('off')
    def box(x, y, w, h, text):
        ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.08',fc='white',ec='black'))
        ax.text(x+w/2,y+h/2,text,ha='center',va='center',size=12)
    def link(a,b,text,yoff=.2):
        ax.annotate('',xy=b,xytext=a,arrowprops={'arrowstyle':'->','color':'black','lw':1})
        ax.text((a[0]+b[0])/2,(a[1]+b[1])/2+yoff,text,ha='center',size=10)
    box(.15,2.6,1.85,.8,'Генератор\nиспытательных сигналов')
    box(4.15,2.6,1.7,.8,'Макет ПОС\n(плата А4.1)')
    box(8.05,2.6,1.8,.8,'ПК регистрации\nи управления')
    box(.35,.53,2.8,.73,'Осциллограф')
    box(3.8,.53,2.4,.73,'Источник 12 В')
    box(7.25,.53,2.6,.73,'Средства программирования')
    link((2.0,3),(4.15,3),'ПЧ → вход АЦП')
    link((5.85,3),(8.05,3),'Ethernet')
    link((4.35,2.6),(2.1,1.26),'выход ЦАП')
    link((5,1.26),(5,2.6),'питание',-.33)
    link((8.4,1.26),(5.7,2.6),'JTAG / SWD')
    ax.text(5,4.0,'Функциональные связи по доступной схеме рабочего места',ha='center',size=12)
    fig.savefig(path,dpi=230,bbox_inches='tight',pad_inches=.09,facecolor='white')
    plt.close(fig)

if __name__ == '__main__':
    render(Path(__file__).with_name('workplace.png'))
