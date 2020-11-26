from PIL import Image
img = Image.open('test1.png')
new_img = img.resize((173,73))
new_img.save('r-test1.png','png')