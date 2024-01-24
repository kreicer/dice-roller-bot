parsing_regexp = r'^(?P<mod>[+-]*)?' \
                 r'(?P<throws>\d*)?' \
                 r'(?P<delimiter>d|$)' \
                 r'(?P<edge>\d*|[fF]$)' \
                 r'(?P<separator>/|$)' \
                 r'(?P<postfix>[a-z]*)?' \
                 r':?' \
                 r'(?P<value>\d*)?$'
