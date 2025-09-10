REGEX_CHECK = (
    r'^('  # start at start
    r'[\x09\x0A\x0D\x20-\x7E]'  # ASCII
    r'|[\xC2-\xDF]'  # non-overlong 2-byte
    r'|[\xE0\xA0-\xBF]'  # excluding overlongs
    r'|[\xE1-\xEC\xEE\xEF]{2}'  # straight 3-byte
    r'|[\xED\x80-\x9F]'  # excluding surrogates
    r'|[\xF0\x90-\xBF]{2}'  # planes 1-3
    r'|[\xF1-\xF3]{3}'  # planes 4-15
    r'|[\xF4\x80-\x8F]{2}'  # plane 16
    r')*$')  # match all until end

REGEX_ERROR_MESSAGE = "Invalid character used"
