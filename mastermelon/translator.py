from translate import Translator
def translate(message):
    translator = Translator(to_lang="en")
    return translator.translate(message)
