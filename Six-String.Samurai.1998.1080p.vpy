import vapoursynth as vs
import awsmfunc as awf
import rekt as rk
import btpfunc as btp
import vsutil
import kagefunc as kgf
import fvsfunc as fvf
import adptvgrnMod as adp
core = vs.get_core()

core.num_threads = 4
core.max_cache_size = 2048

#Importing source
path=r'D:\test\Six-String.Samurai.1998.1080p.BluRay.Remux.AVC.DTS-HD.MA.5.1-PmP.mkv'
src=core.ffms2.Source(path)

#Dither
src=vsutil.depth(src,16)

#Cropping
src=video=core.std.CropRel(src,left=0, top=22, right=0, bottom=22)

#Fixing dirty lines
src=core.cf.ContinuityFixer(src, [0,0,0], [3,2,2], [0,0,0], [3,2,2], [60,40,40])
src=awf.fb(src, left=2, top=2, right=2, bottom=2)
src=rk.rektlvls(src,rownum=None,rowval=None,colnum=[0,1,1918,1919],colval=[1,1,1,1], prot_val=20)

#Extracting luma plane for the mask
y=vsutil.get_y(src)

#For debanding the logo and some intro scenes containing the explosion
intromask=kgf.retinex_edgemask(src).std.Binarize(45000).std.Maximum().std.Maximum().std.Maximum().std.Inflate()
deb=core.neo_f3kdb.Deband(src,range=20,y=64,cb=48,cr=48,grainy=10,grainc=10,dynamic_grain=True,output_depth=16, keep_tv_range=True)
deb=adp.adptvgrnMod(deb,strength=1.2,cstrength=1.2,sharp=70,size=1.15,static=False,luma_scaling=6,grain_chroma=True,grainer=None,fade_edges=True,tv_range=True)
deb=core.std.MaskedMerge(src,deb,intromask)
src=fvf.ReplaceFrames(src,deb,"[0 1102]")

"""
Now dealing with the most problematic scenes. In my previous encode of this same movie I used kagefunc's retinex_edgemask which failed miserably since these scenes has high luma distortion and moderate distortion across chroma.
So I need a mask to detect the rate of change of gradient not to detect gradient change."""

#First defining 5*5 sobel mask to detect edges i,e performing close approximate of first order derivative to detect gradient change.
sx=core.std.Convolution(y,[-5,-4,0,4,5,-8,-10,0,10,8,-10,-20,0,20,10,-8,-10,0,10,8,-5,-4,0,4,5])
sy=core.std.Convolution(y,[-5,-8,-10,-8,-5,-4,-10,-20,-10,-4,0,0,0,0,0,4,10,20,10,4,5,8,10,8,5])

"""
Now I need to find the rate of change of gradient. This can be done by using four extended laplacian parameters or running the sobel 5*5 twice along both horizontal and vertical direction.
I chose 3*3 Sobel mask this time because using 5*5 due to the presence of heavy grain will detect outliers or will simply pickup noise whic I don't need. In short this detects ridges.
For high grain source like this muvsfunc's ridge detection is also good but it simply pickup too much noise running Knn_means_cl afterwards to denoise is preferable but it's also slow so I avoided this approach."""

#Performing higher order partial derivative to detect ridges.
sxx=core.std.Convolution(sx,[-3, 0, 3, -10, 0, 10, -3, 0, 3])
sxy=core.std.Convolution(sy,[-3, 0, 3, -10, 0, 10, -3, 0, 3])
syx=core.std.Convolution(sx,[-3, -10, -3, 0, 0, 0, 3, 10, 3])
syy=core.std.Convolution(sy,[-3, -10, -3, 0, 0, 0, 3, 10, 3])

#Using Flow-based Difference Of Gaussian operator to extract edges(since it's low pass it's resistant to noise) as a support to the ridge detection mask by adding it to the ridge detection mask and clamped it to 16 bit depth. 
FDOG=[[1, 1, 0, -1, -1, 2, 2, 0, -2, -2, 3, 3, 0, -3, -3, 2, 2, 0, -2, -2, 1, 1, 0, -1, -1],
[1, 2, 3, 2, 1, 1, 2, 3, 2, 1, 0, 0, 0, 0, 0, -1, -2, -3, -2, -1, -1, -2, -3, -2, -1]]

#Convolving and finding the magnitude of FDOG
mag=[core.std.Convolution(y,m[:25],divisor=2,saturate=False)for m in FDOG]
mag=core.std.Expr(mag,'x dup * y dup * + sqrt')

res=core.std.Expr([sxx,sxy,syx,syy,mag],'x abs y abs max z abs max a abs max b + 65535 min')#Finding max rate of change of gradient add the FDOG operator and clamping it to 16 bit.

#Inverting the mask as it helps me to visualize where I want to deband and using expr to binarize the mask.
mask=core.std.Invert(res).std.Expr('x 60000 > x 0 ? ')

#Debanding and using adptvgrMod to compress the added grain more also helps a bit in deblocking.
deband=core.neo_f3kdb.Deband(src,range=26,y=250,cb=200,cr=200,grainy=50,grainc=50,dynamic_grain=True,output_depth=16, keep_tv_range=True)
deband=adp.adptvgrnMod(deband,strength=1.2,cstrength=1.2,sharp=60,size=0.65,static=False,luma_scaling=6,grain_chroma=True,grainer=None,fade_edges=True,tv_range=True)
deband=core.std.MaskedMerge(src,deband,mask)#debanding whiter regions given by the mask
src=fvf.ReplaceFrames(src,deband,"[82427 90619]")
src=vsutil.depth(src,8,dither_type='error_diffusion')

#test
#test=src[82427:90620] for testing problematic scenes
#test.set_output()
#src=awf.SelectRangeEvery(src, every=15000, length=250, offset=[1000, 5000]) #for testing random frames

#output
src.set_output()
