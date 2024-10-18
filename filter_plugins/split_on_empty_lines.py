def split_on_empty_lines(value):
    returnlist = []
    for section in value.split("\n\n"):
        if section.strip():
            returnlist.append(section.strip())
    return returnlist


class FilterModule(object):
    def filters(self):
        return {"split_on_empty_lines": split_on_empty_lines}
