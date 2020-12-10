from PIL import Image
img = Image.open('../data_in/0.png')
new_img = img.resize((1600,120))
new_img.save('../data_in/0.png','png')