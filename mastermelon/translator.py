from translate import Translator #! Import module

def translating(message):
    translator = Translator.translate(to_lang="en")
    return translator.translate(message)
