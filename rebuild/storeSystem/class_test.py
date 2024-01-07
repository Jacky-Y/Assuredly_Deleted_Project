from overwirter_class import VideoOverwriter
from overwirter_class import ImageOverwriter
from overwirter_class import AudioOverwriter
from overwirter_class import JsonOverwriter
from overwirter_class import TextOverwriter
# videoOverwriter = VideoOverwriter(alg_param="sIWCe8HqjYDZN+Z/5/yXaw1qe8f9j6SCWAlSNHFZqs8=",level=1)
# videoOverwriter.overwrite_file(target_files=['./2023-07-20-2027-43.mp4'])

imageOverwriter=JsonOverwriter(granularity=None,alg_param="sIWCe8HqjYDZN+Z/5/yXaw1qe8f9j6SCWAlSNHFZqs8=",level=1)
imageOverwriter.command_delete(['./storeSystem/f/url1.png','./storeSystem/f/url2.png'])

print("done")

