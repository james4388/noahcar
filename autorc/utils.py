
def range_map(value, in_min, in_max, out_min, out_max, int_only=False):
    '''To map the value from a range to another'''
    new_value = (
        (value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min
    )
    if int_only:
        return int(new_value)
    return new_value
