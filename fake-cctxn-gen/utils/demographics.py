def make_cities(base_home):
    cities = {}
    locations_reference_path = base_home + "/data/reference_data/locations_partitions.csv"
    f = open(locations_reference_path, 'r').readlines()
    for line in f:
        try:
            cdf, output = line.replace('\n', '').split(',')
            cities[float(cdf)] = output
        # header
        except:
            pass
    return cities


def make_age_gender_dict(base_home):
    gender_age = {}
    prev = 0
    demographics_reference_path = base_home + "/data/reference_data/age_gender_demographics.csv"
    f = open(demographics_reference_path, 'r').readlines()
    for line in f:
        l = line.replace('\n', '').split(',')
        if l[3] != 'prop':
            prev += float(l[3])
            gender_age[prev] = (l[2], float(l[1]))
    return gender_age
