import os.path


checkDirs = ['words/', 'words/a01/a01-000u/']
checkFiles = ['words.txt', 'rf-test1.png', 'words/a01/a01-000u/a01-000u-00-00.png']


for f in checkDirs:
	if os.path.isdir(f):
		print('[OK]', f)
	else:
		print('[ERR]', f)


for f in checkFiles:
	if os.path.isfile(f):
		print('[OK]', f)
	else:
		print('[ERR]', f)
