import vapoursynth as vs
import kagefunc as kgf
import awsmfunc as awf
from adptvgrnMod import adptvgrnMod 
import havsfunc as hvf
from rekt import rektlvls
from vsutil import iterate,depth,get_y
from pathlib import Path
import fvsfunc as fvf

core = vs.get_core()

path=Path("D:\Test\Battle.Beyond.the.Stars.1980.1080p.BluRay.Remux.AVC.DTS-HD.MA.5.1-PmP.mkv")

#importing video
src=video=core.lsmas.LWLibavSource(path)

#Cropping black bars
src=core.std.Crop(src,top=22,left=0,bottom=22,right=0)

#dither
src=depth(src,16)

#Fixing dirty lines
src=core.fb.FillBorders(src,left=1,top=0,right=2,bottom=0)
src=rektlvls(src, rownum=None, rowval=None, colnum=[1913,1914,1915,1916,1917,1918,1919], colval=[2]*7, prot_val=[16, 235])

#Debanding the logo
logomask=kgf.retinex_edgemask(src).std.Binarize(5000).std.Maximum()
deband=core.f3kdb.Deband(src,y=48,cb=48,cr=49,grainy=30,grainc=30,dynamic_grain=True)
deband=adptvgrnMod(deband,strength=0.8,cstrength=0.7,size=1.1,sharp=35,static=False,luma_scaling=5,grain_chroma=True)
deband=core.std.MaskedMerge(src,deband,logomask)
src=fvf.rfs(src,deband,"[60 191]")

#Fixing credits,sharpening,dehaloing and whitening
y=get_y(src)
warpmask=core.std.Sobel(y).std.Binarize(50000).std.Maximum().std.Maximum().std.Inflate()
warp=core.warp.AWarpSharp2(src)
warp=core.std.MaskedMerge(src,warp,warpmask)
dehalomask=hvf.FineDehalo(get_y(warp),showmask=4)
mask_outer=iterate(dehalomask, core.std.Maximum, 2)
mask_inner=iterate(mask_outer, core.std.Minimum, 3)
halos=core.std.Expr([mask_outer, mask_inner], 'x y -')
dh=hvf.DeHalo_alpha(warp,rx=1.5,ry=1.5)
warp=core.std.MaskedMerge(warp,dh,halos).std.Expr('x 50000 >= 65535 x ?')
src=fvf.rfs(src,warp,"[144502 147605]")

#dithering down to 8 bit
src=depth(src,8,dither_type='ordered')

#for test encodes
#src=awf.SelectRangeEvery(src,every=3000,length=50,offset=10000)

#output
src.set_output()

