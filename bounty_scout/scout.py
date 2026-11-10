    # number of domain keywords matched
    keywords = _weights(text, KEYWORDS)
    # number of penalty keywords matched
    penalties = _weights(text, PENALTIES)
    return sum(keywords), sum(penalties)