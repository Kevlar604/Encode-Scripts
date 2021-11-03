import vapoursynth as vs
from muvsfunc import SSIM_downsample
import awsmfunc as awf
from cooldegrain import CoolDegrain
import lvsfunc as lvf
import kagefunc as kgf
from adptvgrnMod import *
from havsfunc import FineDehalo
from vsutil import depth,split,join
import btpfunc as btp
import fvsfunc as fvf

core = vs.get_core()
core.num_threads = 4
core.max_cache_size = 2048


#Source
src=core.lsmas.LWLibavSource(r'D:\Test\Violet.Evergarden.The.Movie.2020.UHD.BluRay.REMUX.2160p.TrueHD.Atmos.7.1.DV.HEVC-CHPOSTALCOMPANY\Violet.Evergarden.The.Movie.2020.UHD.BluRay.REMUX.2160p.TrueHD.Atmos.7.1.DV.HEVC-CHPOSTALCOMPANY_track1_[und].hevc')

#Cropping
src=core.std.Crop(src, top=276, bottom=276)

#Finding new height after cropping for the purpose of resizing
nh=round(1920 /src.width / 2 * src.height)* 2


src=depth(src,16)

#Deringing and dehaloing
src=core.warp.AWarpSharp2(src, type=1, depth=[6,3,3], thresh=64, cplace="mpeg2") #Sharpening
dh=FineDehalo(src,darkstr=0,brightstr=0.7,showmask=0,thmi=20,thma=100,rx=2.4,ry=2.4) #Dehaloing

#Selectively applying the filters
src=src.std.Trim(0, 605)+dh.std.Trim(606, 1210)+src.std.Trim(1211, 1547)+dh.std.Trim(1548, 14782)+src.std.Trim(14783, 15198)+dh.std.Trim(15199, 190652)+src.std.Trim(190653, 200716)+dh.std.Trim(200717, 201299)+src.std.Trim(201300, 201527)

#Splitting luma and chroma planes
y,u,v=split(src)

#Descaling luma
y=fvf.Debicubic(y,1920,nh,b=0,c=0.5)

#Hopefully the shift is correct
shift=0.25-0.25*3840/1920

#Resizing chroma
u, v = u.resize.Spline36(960,nh/2, src_left=shift), v.resize.Spline36(960,nh/2, src_left=shift)

#Joining luma and chroma planes
src=join([y,u,v])

#Aicha's port of vardefunc's dumb3kdb
def f32kdb(clip, range=18, y=48, cb=48, cr=48, sample_mode=4, dither="none"):
    """
    just an easier to read version of vardefunc's dumb3kdb with minor changes:
    * grain is always 0
    * changed defaults
    * clips are merged at 32-bit
    * you can also just pass a 32-bit clip (Idc if this is slower or something)
    """
    from vsutil import depth
    # 16 for sample_mode = 2
    # 32 for rest
    step = 16 if sample_mode == 2 else 32

    odepth = max(clip.format.bits_per_sample, 16)
    clip = depth(clip, 16, dither_type="none")

    if y % step == cb % step == cr % step == 0:
        return depth(clip.neo_f3kdb.Deband(range, y, cb, cr, 0, 0, sample_mode), odepth, dither_type=dither)
    else:
        loy, locb, locr = [max((th - 1) // step * step + 1, 0) for th in [y, cb, cr]]
        hiy, hicb, hicr = [min(lo + step, 511) for lo in [loy, locb, locr]]

        lo_clip = depth(clip.neo_f3kdb.Deband(range, loy, locb, locr, 0, 0, sample_mode), 32)
        hi_clip = depth(clip.neo_f3kdb.Deband(range, hiy, hicb, hicr, 0, 0, sample_mode), 32)

        if clip.format.color_family == vs.GRAY:
            weight = (y - loy) / step
        else:
            weight = [(y - loy) / step, (cb - locb) / step, (cr - locr) / step]

        return depth(core.std.Merge(lo_clip, hi_clip, weight), odepth, dither_type=dither)

#denoising
pf = core.dfttest.DFTTest(src, sigma=1, tbsize=3, opt=3, planes=[0,1,2])
denoise = CoolDegrain(src, tr=1, thsad=8, thsadc=4, bits=16, blksize=8, overlap=4, pf=pf)

#Debanding
db=f32kdb(denoise)

#Detail preserving edgemask
mask=kgf.retinex_edgemask(src, sigma=0.2)

#Masked filtering with the help of edgemask
db=core.std.MaskedMerge(db,src,mask)

#Adding grains to the grain starved debanded scenes
db=adptvgrnMod(db,strength=1,cstrength=1,grain_chroma=True,size=.5,sharp=80,static=True,luma_scaling=40,seed=3)

#Finally dithering down to 10 bit depth
src=depth(db,10,dither_type='error_diffusion')
src.set_output() #output
