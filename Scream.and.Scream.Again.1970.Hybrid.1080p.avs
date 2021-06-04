b=FFVideoSource("D:\Sync\Scream.and.Scream.again.1970.mkv") #Kino Lorber Source
b=b.trim(278,b.FrameCount()-1)
b=b.crop(2,20,-2,-20)
b=b.FixCBr(0,-10).FillBorders(2,0,0,0)
b=b.FixRBr(2,8).FixRBr(1,-6).FillBorders(0,1,0,0).BalanceBorders(1,0,0,0)
b=b.FixRBr(1037,6).FixRBr(1038,-10).FillBorders(0,0,0,1).BalanceBorders(0,1,0,0)
b=b.FixCBr(1914,5).FixCBr(1915,-3).FillBorders(0,0,2,0)
b1=b
b2=b1
b3=b2
b4=b3
b1=b1.crop(0,1036,0,0) #Extracting bottom edge
b2=b2.crop(0,0,0,-1036) #Extracting top edge
b3=b3.crop(1912,0,0,0) #Extracting right edge
b4=b4.crop(0,0,-1912,0) #Extracting left edge
a=FFVideoSource("D:\Test\VideoScream.mkv") #Twilight Time source
a=a.crop(2,24,-2,-24) #Cropping black borders and top and bottom edges 
c=StackVertical(b2,a,b1) #stacking top and bottom edges from KL souce to the Twilight Time Blu-ray
c=c.crop(4,0,-4,0) #Cropping left and right edges 
d=StackHorizontal(b4,c,b3) #stacking left and right edges from KL souce to the Twilight Time Blu-ray
#overlaying KL over Twilight Time
e=Overlay(d,b,x=0,y=0,opacity=0.65,mode="blend",greymask=true,ignore_conditional=false,pc_range=false)
#Overlaying Twilight Time over KL
f=Overlay(b,d,x=0,y=0,opacity=0.55,mode="blend",greymask=true,ignore_conditional=false,pc_range=false)
#deblocking and debanding
e=e.f3kdb(range=25,grainY=10,Y=64) 
Concatenating all the fixed parts along with the remaining frames
b=b.trim(0,34318)+e.trim(34319,38211)+b.trim(38212,38221)+f.trim(38222,42939)+b.trim(42940,b.FrameCount()-1)
b
