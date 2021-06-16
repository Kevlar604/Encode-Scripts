import vapoursynth as vs
import awsmfunc as awf
import rekt as rk
import btpfunc as btp
import vsutil
import Oyster as oys
import kagefunc as kgf
import fvsfunc as fvf
import adptvgrnMod as adp
core = vs.get_core()

path=r'D:\Sync\Six-String.Samurai.1998.1080p.BluRay.Remux.AVC.DTS-HD.MA.5.1-PmP.mkv'
src=core.ffms2.Source(path)
src=vsutil.depth(src,16)
src=core.std.CropRel(src,left=0, top=22, right=0, bottom=22)
src=core.cf.ContinuityFixer(src, [0,0,0], [3,2,2], [0,0,0], [3,2,2], [60,40,40])
src=awf.fb(src, left=2, top=2, right=2, bottom=2)
src=rk.rektlvls(src,rownum=None,rowval=None,colnum=[0,1,1918,1919],colval=[1,1,1,1], prot_val=20)
mask=kgf.retinex_edgemask(src).std.Binarize(45000).std.Maximum().std.Maximum().std.Maximum().std.Inflate()
deband=core.neo_f3kdb.Deband(src,range=26,y=250,cb=200,cr=200,grainy=30,grainc=20,dynamic_grain=True,output_depth=16, keep_tv_range=True)
video=core.std.MaskedMerge(deband,src,mask)
video=adp.adptvgrnMod(video, strength=2,cstrength=1,size=1,sharp=25, static=False, luma_scaling=5, grain_chroma=True, grainer=None, fade_edges=True, tv_range=True, protect_neutral=True, seed=-1, show_mask=False)
src=fvf.ReplaceFrames(src,video,"[82427 90619]")
src=vsutil.depth(src,8,dither_type='error_diffusion')
#src=awf.SelectRangeEvery(src, every=15000, length=250, offset=[1000, 5000])
src.set_output()

    
    


