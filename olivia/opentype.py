from fonts import hb

def ot_feature(name):
    b, O = hb.feature_from_string(list(map(ord, name)))
    if b:
        return O
    else:
        raise ValueError('invalid opentype feature name ' + repr(name))

common_features = ['calt', 'case', 'c2pc', 'c2sc', 'hlig', 'ital', 'kern', 'liga', 'mgrk', 'onum', 'pcap', 'pnum', 'rand', 'salt', 'smcp', 'subs', 'sups', 'swsh', 'titl', 'tnum', 'unic', 'zero']
feature_map = {feature: ot_feature(feature) for feature in common_features}
