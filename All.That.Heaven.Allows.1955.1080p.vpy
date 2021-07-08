import vapoursynth as vs
from vsTAAmbk import *
from rekt import rektlvls
import adptvgrnMod 
import awsmfunc as awf
import fvsfunc as fvf
import kagefunc as kgf
from vsutil import depth

core = vs.get_core()
src=r'E:\Movies\All.That.Heaven.Allows.1955.BluRay.Remux.The.Criterion.Collection.1080p.AVC.FLAC.1.0-PJX.mkv'
src=core.lsmas.LWLibavSource(src)
src=depth(src,16)
src=core.std.CropRel(src, left=16, right=16, top=0, bottom=0)
#Fixing 3px dirty line accross the chroma plain and merging them with the luma
fix=core.cf.ContinuityFixer(src,left=[0,3,3],right=[0,3,3],top=[0,0,0],bottom=[0,0,0])
src=core.std.Merge(src,fix, weight=[0,1])
#Fixing 1px dirty line's luma brightness
src=rektlvls(src,rownum=None, rowval=None, colnum=[0,1879], colval=[4,4], prot_val=[16, 235])
#Fillbordering 1px dirty line at the bottom
src=core.fb.FillBorders(src, left=0, right=0, top=0, bottom=1)
#Antialiasing for scenes where information about the cast and crew are shown
taa=TAAmbk(src,aatype='Nnedi3')
src=fvf.rfs(src,taa,"[600 2500]")
#debanding the logo scenes
mask = kgf.retinex_edgemask(src).std.Binarize(8000).std.Maximum()
deband=core.f3kdb.Deband(src,y=60,cb=60,cr=60,grainy=48,grainc=48,dynamic_grain=True,range=16)
deband=adptvgrnMod.adptvgrnMod(deband, strength=1.00, size=1.25, sharp=50, static=False, luma_scaling=25,grain_chroma=False, grainer=None, show_mask=False)
deband=core.std.MaskedMerge(deband, src, mask)
src=fvf.rfs(src,deband,"[0 560]")
src=depth(src,8,dither_type='error_diffusion')
src.set_output()
