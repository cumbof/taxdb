
taxonomy = {
    "city": {
        "part_of": "region"
    },
    "region": {
        "part_of": "state"
    },
    "state": {
        "part_of": "continent"
    },
    "lazio": {
        "is_a": "region"
    },
    "lombardia": {
        "is_a": "region"
    },
    "rome": {
        "is_a": "city"
    },
    "milan": {
        "is_a": "city"
    },
    "naples": {
        "is_a": "city"
    },
    "san raffaele": {
        "part_of": "rome"
    },
    "ieo": {
        "part_of": "milan"
    }
}

dataset_columns = [ 'sequencing_center', 'race', 'gender' ];
dataset = {
    "row1": {
        "sequencing_center": "san raffaele",
        "race": "hispanic or latino",
        "gender": "male"
    },
    "row2": {
        "sequencing_center": "san raffaele",
        "race": "hispanic or latino",
        "gender": "female"
    },
    "row3": {
        "sequencing_center": "ieo",
        "race": "hispanic or latino",
        "gender": "male"
    }
}
print "dataset:";
print dataset;

query = "SELECT * FROM dataset WHERE city = \'milan\'";
print "query: " + query;

WHERE_key = "city";
WHERE_value = "milan";

extended_dataset = { };

if WHERE_key in dataset_columns:
    for row in dataset:
        if dataset[row][WHERE_key] == WHERE_value:
            extended_dataset[row] = dataset[row];
else: # use taxonomy
    # search for WHERE_key in taxonomy
    is_a_map = { };
    if WHERE_key in taxonomy: # if WHERE_key exists in taxonomy, search for elements in a 'is_a' relation with WHERE_key
        for elem in taxonomy:
            if 'is_a' in taxonomy[elem]:
                if taxonomy[elem]['is_a'] == WHERE_key:
                    values = [ ];
                    if WHERE_key in is_a_map:
                        values = is_a_map[WHERE_key];
                    values.append( elem );
                    is_a_map[WHERE_key] = values;
    print "is_a_map:";
    print is_a_map;
    part_of_map = { };
    if WHERE_value in is_a_map[WHERE_key]:
        for elem in taxonomy:
            if 'part_of' in taxonomy[elem]:
                if taxonomy[elem]['part_of'] == WHERE_value:
                    values = [ ];
                    if WHERE_value in part_of_map:
                        values = part_of_map[WHERE_value];
                    values.append( elem );
                    part_of_map[WHERE_value] = values;
    print "part_of_map:";
    print part_of_map;
    for row in dataset:
        for key in dataset[row].keys():
            for part_of_key in part_of_map:
                if dataset[row][key] in part_of_map[part_of_key]:
                    for is_a_key in is_a_map:
                        if part_of_key in is_a_map[is_a_key]:
                            extended_dataset[row] = dataset[row];
                            extended_dataset[row][is_a_key] = part_of_key;
print "extended_dataset:";
print extended_dataset;
