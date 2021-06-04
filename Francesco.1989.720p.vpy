import vapoursynth as vs
import havsfunc as hvf
import kagefunc as kgf
import vsutil
import kashfunc as ksh #my own python module for vapoursynth will releaase it publicly soon still a lot of work to do
import fvsfunc as fvf
import adptvgrnMod as adp
core = vs.get_core()
video=core.lsmas.LWLibavSource(r'D:\Video\UNNAMED DISC\title_t00.mkv')
#Fixing dirty lines by extracting each plane and fixing them individually
l=vsutil.get_y(video)#luma plane
u=vsutil.plane(video,1)
v=vsutil.plane(video,2)
l=core.edgefixer.ContinuityFixer(l,2,2,2,0,10)
u=core.edgefixer.ContinuityFixer(u,1,1,1,0,5)
v=core.edgefixer.ContinuityFixer(v,1,1,1,0,5)
video1=core.std.ShufflePlanes([l,u,v],[0,0,0],colorfamily=vs.YUV)#merging the planes together
video1=core.resize.Spline36(video1, width=1280, height=720)
video3=vsutil.depth(video1,16)
luma=core.std.ShufflePlanes(video3, [0], colorfamily=vs.GRAY)#extracting luma plane
gblur=core.bilateral.Gaussian(luma,[3.0,0,0],[3.0,0,0])#performing Gausian blur so that our mask doesn't pickup useless stuffs especialy noise 
#Defining a Kirsch mask by taking an arbitary point and rotating by 45 degrees in each 8 directions
k1 = core.std.Convolution(gblur,[ 5,  5,  5, -3,  0, -3, -3, -3, -3])
k2 = core.std.Convolution(gblur,[-3,  5,  5,  5,  0, -3, -3, -3, -3])
k3 = core.std.Convolution(gblur,[-3, -3,  5,  5,  0,  5, -3, -3, -3])
k4 = core.std.Convolution(gblur,[-3, -3, -3,  5,  0,  5,  5, -3, -3])
k5 = core.std.Convolution(gblur,[-3, -3, -3, -3,  0,  5,  5,  5, -3])
k6 = core.std.Convolution(gblur,[-3, -3, -3, -3,  0, -3,  5,  5,  5])
k7 = core.std.Convolution(gblur,[ 5, -3, -3, -3,  0, -3, -3,  5,  5])
k8 = core.std.Convolution(gblur,[ 5,  5, -3, -3,  0, -3, -3,  5, -3])
kirsch=core.std.Expr([k1, k2, k3, k4, k5, k6, k7, k8], 'x y max z max a max b max c max d max e max')#Finding maximum slope along a particular direction(North,North-West,West,South-West,South,South-East,East and North-East) which is essentially the max of first order partial derivative in eight different directions.
#Performing hysteresis on the resultant mask by sharpening and brightening the edgemask, bit of a lazy way however it kinda works so be it and I'm tired :p Will improve it further in my own python module kashfuc.py. What it does is it removes useless stuffs which does not require fixing.
sharpen=core.std.Convolution(kirsch,[0,-1,0,-1,5,-1,0,-1,0],planes=[0],saturate=False).std.Expr('x 65535 / sqrt 65535 *')
m1=vsutil.iterate(sharpen, core.std.Maximum, 2)#Maximizing the mask twice   
m2=vsutil.iterate(m1, core.std.Minimum, 3)#Minimizing the expanded max thrice  
halos=core.std.Expr([m1,m2], 'x y -').std.Inflate().std.Inflate()#Subtracting the maximized mask from the minimized mask to cover only the halos.
dehalo1=hvf.FineDehalo(video3)#Performing dehaloing
dehalo2=hvf.DeHalo_alpha(video3)#using another filter to dehalo
d=ksh.MaxFilter(video3,dehalo1,dehalo2,strict=True)#Inspired from Kgarbs MaxFilter https://github.com/kgrabs/zzfunc when strict is set to 'True' it averages the output of two filters. Will modify it more in Kashfunc.py to perform Weighted average filtering.
d=core.std.MaskedMerge(video3,d,halos)#Masked dehaloing 
d=vsutil.depth(d,8,dither_type='error_diffusion')#dithering down to 8 bit

#Trying another method to dehalo
video2=hvf.FineDehalo(vsutil.depth(video1,16),showmask=4).std.Maximum().std.Maximum()#Extrating FineDehalo's strong mask
video5=video2.std.Minimum().std.Minimum().std.Minimum()
stronghalo=core.std.Expr([video2,video5], 'x y -').std.ShufflePlanes([0], colorfamily=vs.GRAY).std.Inflate().std.Inflate()
video6=vsutil.depth(video1,16)
dh=hvf.DeHalo_alpha(video6,rx=2.5,ry=2.5)
dh=core.std.MaskedMerge(video6,dh,stronghalo)
dh=vsutil.depth(dh,8,dither_type='error_diffusion')

finaldehalo=ksh.MaxFilter(video1,d,dh,strict=False)#visually both the filtration method gave almost similar results but I don't want to take chances hence taking the maximum outcome of either of the two filters by setting Strict=False

video4=finaldehalo
video4=vsutil.depth(video4,16)
#n=video4.num_frames
#thresh = (32 * (1 << video4.format.bits_per_sample) - 1) / 255
mask=kgf.retinex_edgemask(video4).std.Maximum().std.Inflate().std.Maximum().std.Inflate()
#deblocking and debanding by adding some grain across the luma and chroma planes.
deband = core.neo_f3kdb.Deband(video4, y=128, cb=64, cr=64, range=25, grainy=32,grainc=20, output_depth=16, keep_tv_range=True)
#Modyifying the added grain a bit to compress better and not look like a mosquito noise or whatever it is called!
deband=adp.adptvgrnMod(deband, strength=2, size=1.5, sharp=25, static=False,luma_scaling=5, grain_chroma=True)
merge=core.std.MaskedMerge(deband,video4,mask)#masked 
merge=vsutil.depth(merge,8,dither_type='error_diffusion')

#6232 #11270-36308/2 97398/2 104680-110896/2 136606-144942 163034-168926/2 176062-180412/2 207896-220054/2 #252366-257132 373936-374918/2 
#Applying the filters by replacing the original frames with the filtered frames.
video1=fvf.rfs(video1,finaldehalo,"[3116 187459]")
video1=fvf.rfs(video1,merge,"[5635 18154][52340 55448][58388 58859][59518 59818][68303 72471][81517 84463][88031 90206][103948 110027][126183 128566][185914 187459]") 

video1.set_output()
