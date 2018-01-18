import yaml

class folded_unicode(unicode): pass
class literal_unicode(unicode): pass

def folded_unicode_representer(dumper, data):
    return dumper.represent_scalar(u'tag:yaml.org,2002:str', data, style='>')
def literal_unicode_representer(dumper, data):
    return dumper.represent_scalar(u'tag:yaml.org,2002:str', data, style='|')

yaml.add_representer(folded_unicode, folded_unicode_representer)
yaml.add_representer(literal_unicode, literal_unicode_representer)

data = {
    'liter':literal_unicode(
        u'by hjw              ___\n'
         '   __              /.-.\\\n'
         '  /  )_____________\\\\  Y\n'
         ' /_ /=== == === === =\\ _\\_\n'
         '( /)=== == === === == Y   \\\n'
         ' `-------------------(  o  )\n'
         '                      \\___/\n'),
    'folded': folded_unicode(
        u'It removes all ordinary curses from all equipped items. '
        'Heavy or permanent curses are unaffected.\n')}

print yaml.safe_dump(data)
