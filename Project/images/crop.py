from PIL import Image
import os

def crop(infile,height,width):
    im = Image.open(infile)
    imgwidth, imgheight = im.size
    for i in range(height):
        for j in range(width):
            box = (j*(imgwidth // width), i*(imgheight // height), (j+1)*(imgwidth // width), (i+1)*(imgheight // height))
            yield im.crop(box)

if __name__=='__main__':
    infile=input('infile ')
    height=int(input('height '))
    width=int(input('width '))
    start_num=int(input(('strart_num ')))
    im = Image.open(infile)
    imgwidth, imgheight = im.size
    for k,piece in enumerate(crop(infile,height,width),start_num):
        img=Image.new('RGBA', (imgheight // height, imgwidth // width), 255)
        img.paste(piece)
        path=os.path.join(f"{infile[:-4]}-{k}.png")
        img.save(path)