from googletrans import Translator

translator = Translator()
info = translator.translate('little', src='en', dest='es')
print(info.text)
