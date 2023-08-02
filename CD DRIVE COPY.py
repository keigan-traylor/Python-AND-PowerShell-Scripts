import os
import shutil
#The Source Main Folder I Want To Copy
src = "C:"
#Where I Want To Copy The Main Folder
dst = "D:"
#using the os.walk() method I walk through the src folder copying the files and file structure from the src folder. Next I force install it on the dst folder preserving folder structure#
for root, dirs, files in os.walk(src):
    for file in files:
        src_file = os.path.join(root, file)
        dst_file = src_file.replace(src, dst)
        if not os.path.exists(os.path.dirname(dst_file)):
            os.makedirs(os.path.dirname(dst_file))
        shutil.copy2(src_file, dst_file)

