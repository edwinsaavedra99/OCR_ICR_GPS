from PIL import Image
img = Image.open('../data_in/0.png')
new_img = img.resize((473,373))
new_img.save('../data_in/0.png','png')