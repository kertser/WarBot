from spellchecker import SpellChecker
spell = SpellChecker(language='ru')
input = '02ривет киса'
corrected = " ".join([spell.correction(word) for word in input.split()])

print(corrected)