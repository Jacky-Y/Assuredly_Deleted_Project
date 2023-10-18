def generate_delete_command(deleteMethod, max_level=None):
    # 根据deleteMethod来判断
    if deleteMethod == "logicallyDelete":
        return "rm"
    elif deleteMethod == "overwrittenDelete":
        return "shred -n 3 -u"
    elif not deleteMethod:  # 如果deleteMethod为空
        if max_level is not None and max_level >= 5:
            return "shred -n 5 -u"
        else:
            return "shred -n 3 -u"
    else:
        raise ValueError("Invalid deleteMethod provided")