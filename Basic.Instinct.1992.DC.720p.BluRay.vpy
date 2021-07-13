import vapoursynth as vs
import fvsfunc as fvf
from rekt import rekt_fast
import numpy as np
import awsmfunc as awf
from vsutil import *
from adptvgrnMod import *
import kagefunc as kgf
import awsmfunc as awf
from pathlib import Path
core = vs.get_core()

path=Path('D:\\Test\\Basic.Instinct.1992.DC.1080p.BluRay.REMUX.AVC.DTS-HD.MA.5.1-BLURANiUM.mkv')
src=core.lsmas.LWLibavSource(path)
src=video=core.std.Crop(src,0,0,138,138)
video=core.resize.Spline36(video,1280,536,dither_type='error_diffusion')
src=depth(src,16)

#Fixing dirty lines
src=core.cf.ContinuityFixer(src,top=[3,3,3],bottom=[3,3,3],radius=60)
src=core.fb.FillBorders(src, left=1, right=1, top=3, bottom=3,mode="fillmargins")

#Resizing
h=round(1280 / src.width / 2 * src.height) * 2
src=core.resize.Spline36(src,1280,h,dither_type='error_diffusion')

#Extracting luma plane for the masks
y=get_y(src)

#Defining Extended Russell Kirsch compass operator(5*5 matrices)for better detection of edges
m=np.array([[9, 9, 9, 9, 9, 9, 5, 5, 5, 9, -7, -3, 0, -3, -7, -7, -3, -3, -3, -7, -7, -7, -7, -7, -7],
   [9, 9, 9, 9, -7, 9, 5, 5, -3, -7, 9, 5, 0, -3, -7, 9, -3, -3, -3, -7, -7, -7, -7, -7, -7],
   [9, 9, -7, -7, -7, 9, 5, -3, -3, -7, 9, 5, 0, -3, -7, 9, 5, -3, -3, -7, 9, 9, -7, -7, -7],
   [-7, -7, -7, -7, -7, 9, -3, -3, -3, -7, 9, 5, 0, -3, -7, 9, 5, 5, -3, -7, 9, 9, 9, 9, -7],
   [-7, -7, -7, -7, -7, -7, -3, -3, -3, -7, -7, -3, 0, -3, -7, 9, 5, 5, 5, 9, 9, 9, 9, 9, 9],
   [-7, -7, -7, -7, -7, -7, -3, -3, -3, 9, -7, -3, 0, 5, 9, -7, -3, 5, 5, 9, -7, 9, 9, 9, 9],
   [-7, -7, -7, 9, 9, -7, -3, -3, 5, 9, -7, -3, 0, 5, 9, -7, -3, -3, 5, 9, -7, -7, -7, 9, 9],
   [-7, 9, 9, 9, 9, -7, -3, 5, 5, 9, -7, -3, 0, 5, 9, -7, -3, -3, -3, 9, -7, -7, -7, -7, -7]])

m=m.flatten()#Converting 2D array to 1D array   
a,b,c,d,e,f,g,h=np.array_split(m,8)#Splitting into 8 parts representing 8 different directions 
S1=core.std.Convolution(y,matrix=a)
S2=core.std.Convolution(y,matrix=b)
S3=core.std.Convolution(y,matrix=c)
S4=core.std.Convolution(y,matrix=d)
S5=core.std.Convolution(y,matrix=e)
S6=core.std.Convolution(y,matrix=f)
S7=core.std.Convolution(y,matrix=g)
S8=core.std.Convolution(y,matrix=h)
s9=core.std.Convolution(y,matrix=[1]*4+[-8]+[1]*4)#for finding positive gradient change(Laplacian mask)
s10=core.std.Convolution(y,matrix=[-1]*4+[8]+[-1]*4)#for negative gradient change(Laplacian)

#Finding maximum luminance
imask=core.std.Expr([S1,S2,S3,S4,S5,S6,S7,S8],'x y max z max a max b max c max d max e max').std.Binarize(60000).std.Maximum().std.Maximum().std.Inflate()
mask=core.std.Expr([s9,s10],'x y max').std.Binarize(40000).std.Maximum()#finding maximum rate of change of gradient along with binarizing and maximizing the mask.

#Debanding
db=core.neo_f3kdb.Deband(src, range=26,y=64,cb=48,cr=48,grainy=10,grainc=10,dynamic_grain=True)#deband
db=adptvgrnMod(db,strength=1.25,cstrength=1.25,size=1.15,static=False,luma_scaling=6)
db=core.std.MaskedMerge(db,src,mask)
db1=core.neo_f3kdb.Deband(src, range=20, y=48, cb=32, cr=32, grainy=10, grainc=0,dynamic_grain=True)
db1=core.std.MaskedMerge(db1,src,imask)
db1=adptvgrnMod(db1, strength=0.5,size=0.8,static=False,luma_scaling=6)
src=fvf.rfs(src,db,"[82794 85615][159145 160585][171442 177499]")
src=fvf.rfs(src,db1,"[103 6298]")


#Adding static grain to very red scenes copied from Aicha's Antiporno script(Thank you Aicha!)
rgb = src.resize.Bilinear(format=vs.RGB48, matrix_in_s="709")
rgb = core.std.Expr(split(rgb), f"x 1.5 * y - z - x 2 * y - min")
rgb = rgb.std.Invert().std.PlaneStats().adg.Mask(20)
grn = sizedgrn(src, strength=.2, cstrength=.1, size=1.5, sharp=60, static=True)
src = src.std.MaskedMerge(grn, rgb)

src=depth(src,8,dither_type='error_diffusion')

#for test encodes
#src=awf.SelectRangeEvery(src, every=3000, length=50, offset=10000)

src.set_output()
