parsing_regexp = r'^(?P<mod>[+-]*)?' \
                 r'(?P<throws>\d*)?' \
                 r'(?P<delimiter>d|$)' \
                 r'(?P<edge>\d*)' \
                 r'(?P<separator>/|$)' \
                 r'(?P<postfix>[a-zA-Z]*)?' \
                 r':?' \
                 r'(?P<value>\d*)?$'