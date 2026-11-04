# 성기사 추가 외형 1~5 색조합 후보 미리보기 (대기 칸에 부위별 색만 입힌 거친 리컬러 — 샘플 제작 참고용, 게임 시트를 만드는 도구 아님)
# 사용: python tools/paladin_palette_preview.py docs/paladin-skin-palette.png
# 부위 = 머리(땋은 꼬리 포함) · 갑옷 · 망토 · 방패 바탕 · 십자 · 망치 · 눈 홍채. 피부·윤곽·흰자는 그대로 (색표: docs/paladin-skin-palette.md)
from PIL import Image, ImageDraw, ImageFont
import numpy as np, colorsys, sys
from scipy import ndimage as ndi
W,H=291,154
im=np.array(Image.open('assets/sprites/merc/paladin_0.webp').convert('RGBA'))[:, :W].astype(float)
a=im[...,3]>200
hsv=np.array([colorsys.rgb_to_hsv(*(p/255)) for p in im[...,:3].reshape(-1,3)]).reshape(H,W,3)
h,s,v=hsv[...,0]*360,hsv[...,1],hsv[...,2]
yy,xx=np.mgrid[0:H,0:W]
outline=v<0.13
skin=a&(h>8)&(h<35)&(s>0.12)&(s<0.5)&(v>0.6)
blue=a&(h>195)&(h<240)&(s>0.3)&~outline&~skin
lowblue=a&(h>=195)&(h<=265)&(s<0.3)&~outline&~skin   # 푸르스름한 은빛 그늘 (머리털·갑옷 그늘)
gray=a&(s<0.2)&(v>0.13)&~outline&~skin
silver=gray|lowblue
eyebox=(xx>=150)&(xx<=173)&(yy>=68)&(yy<=74)          # 두 눈 (흰자·홍채·윤곽)
eyes=(blue|lowblue)&eyebox                            # 홍채만 (흰자 g·윤곽은 그대로)
# 머리털: 꼭대기(41)~왼쪽 땋은 꼬리 끝(84). 왼쪽 어깨 갑옷(x 144~150, y 78~)과 오른쪽 어깨 갑옷(y 82~)은 뺌. 눈 상자도 뺌
hair=silver&~eyebox&(((xx<=143)&(yy<85))|((xx<=150)&(yy<78))|((xx>150)&(xx<=180)&(yy<82)))
# 방패 바탕: 은빛 테두리·검은 윤곽으로 둘러싸여 망토와 끊겨 있으니 가운데(138,112)를 품은 파란 덩어리만
lab,_=ndi.label(blue)
shield=lab==lab[112,138]
inner=ndi.binary_fill_holes(shield)
cross=silver&inner&~shield                           # 방패 안 십자 (그늘까지)
cape=blue&~shield&~eyebox
gold=a&(h>30)&(h<60)&(s>0.3)&(v>0.3)
armor=silver&~hair&~cross&~eyebox
parts={'hair':hair,'armor':armor,'cape':cape,'shield':shield,'cross':cross,'hammer':gold,'eyes':eyes}

def hx(c): c=c.lstrip('#'); return tuple(int(c[i:i+2],16) for i in (0,2,4))
def recolor(spec):
    out=im.copy()
    for k,m in parts.items():
        if k not in spec or spec[k] is None or not m.any(): continue
        r,g,b=hx(spec[k]); th,ts,tv=colorsys.rgb_to_hsv(r/255,g/255,b/255)
        mv=np.median(v[m]); 
        for y,x in zip(*np.where(m)):
            nv=min(1,max(0,tv*(v[y,x]/mv)**0.9))
            ns=min(1,ts*(0.75+0.5*s[y,x]) if s[y,x]>0.1 else ts*(0.8+0.6*(1-v[y,x])))
            out[y,x,:3]=np.array(colorsys.hsv_to_rgb(th,ns,nv))*255
    return out

# (번호, 이름, 부위 색) — 비우면 그대로
VARIANTS=[
 (0,'기본 (은발·청색)',{}),
 (1,'진홍 성전단',  dict(hair='#e8c45a',armor='#c9ccd4',cape='#b8202c',shield='#ece8dc',cross='#b8202c',hammer='#d9a63a',eyes='#3a7bd5')),
 (2,'칠흑 심판관',  dict(hair='#f2f2f0',armor='#3c3d48',cape='#4a2a7a',shield='#22222a',cross='#e2b545',hammer='#8a8f9c',eyes='#c9a033')),
 (3,'숲의 수호자',  dict(hair='#8a3f26',armor='#b78a4e',cape='#2d6b3c',shield='#2f7a46',cross='#d8dde2',hammer='#b07a3a',eyes='#3f9a5a')),
 (4,'태양의 성전사',dict(hair='#2a2630',armor='#eceae0',cape='#f4f0e4',shield='#e0a62a',cross='#f8f6ee',hammer='#e2b23a',eyes='#d08a2a')),
 (5,'장미 기사',    dict(hair='#f09ab8',armor='#d8d9df',cape='#b23a6a',shield='#c43b74',cross='#e8e8ec',hammer='#d98a7a',eyes='#c84a7a')),
]
S=3
sheet=Image.new('RGBA',(len(VARIANTS)*120*S, (120+60)*S),(58,62,70,255))
d=ImageDraw.Draw(sheet)
try: font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',14*S//2+6)
except: font=None
for i,(n,name,spec) in enumerate(VARIANTS):
    f=Image.fromarray(recolor(spec).astype('uint8'),'RGBA').crop((110,38,206,154)).resize((96*S,116*S),Image.NEAREST)
    sheet.paste(f,(i*120*S+7*S,2*S),f)
    d.text((i*120*S+7*S,120*S),f'{n}  {name}',fill=(255,255,255),font=font)
    keys=['hair','armor','cape','shield','cross','hammer']
    for j,k in enumerate(keys):
        c=spec.get(k)
        if c is None: continue
        x=i*120*S+7*S+j*16*S; y=134*S
        d.rectangle((x,y,x+14*S,y+14*S),fill=hx(c),outline=(0,0,0))
    pass
d.text((7*S,152*S),'색 칸 순서: 머리 · 갑옷 · 망토 · 방패 · 십자 · 망치  (피부·윤곽·눈 색만 따로, 이펙트는 그대로)',fill=(200,200,200),font=font)
sheet.save(sys.argv[1])
print('saved')
