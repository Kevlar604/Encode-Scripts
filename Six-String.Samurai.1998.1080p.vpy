import vapoursynth as vs
import awsmfunc as awf
import rekt as rk
import vsutil
core = vs.get_core()

path=r'D:\Sync\Six-String.Samurai.1998.1080p.BluRay.Remux.AVC.DTS-HD.MA.5.1-PmP.mkv'
src=core.ffms2.Source(path)
src=vsutil.depth(src,16)
src=core.std.CropRel(src,left=0, top=22, right=0, bottom=22)
src=core.edgefixer.ContinuityFixer(src, left=0, top=3, right=0, bottom=3, radius=60)
src=awf.fb(src, left=0, top=2, right=0, bottom=2)
src=rk.rektlvls(src,rownum=None,rowval=None,colnum=[0,1],colval=[1,1], prot_val=20)
src=vsutil.depth(src,8,dither_type='ordered')
#src=awf.SelectRangeEvery(src, every=15000, length=250, offset=[1000, 5000])
src.set_output()
