def is_alnum_or_hyphen_or_space(string):
    assert string.replace(" ", "").replace("-", "").isalnum(), "Allowed characters are alphanumerical or hyphen/space"
    return string
