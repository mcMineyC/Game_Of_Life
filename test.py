from lib import convert_functions as cf
"""
bo$2bo$3o!

4bo$
3b3o$
2b2ob2o2$
bobobobo2bo$
2o3bo3b3o$
2o3bo6bo$
10bobo$
8bobo$
9bo2bo$
12bo!
"""
# rle = input("Enter RLE: ")
rle = "4bo$3b3o$2b2ob2o2$bobobobo2bo$2o3bo3b3o$2o3bo6bo$10bobo$8bobo$9bo2bo$12bo!"
width, height = cf.sizer(rle)
print(width, height)

print(cf.easy_RLE_to_txt(rle))
