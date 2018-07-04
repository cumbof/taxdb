import os, json, gzip, cPickle
import ontospy

# set this parameter to False if the local repository
# already contains the ontology serialized objects
LOAD_ONTOLOGIES_FROM_URL = True;

# local metadata and genomics repository
METADATA_BASEPATH = "./metadata/";
METADATA_EXTENSION = "meta";
DATA_BASEPATH = "./genomics/";
DATA_EXTENSION = "bed";
TUMORS = {
    "TCGA": [
        "ACC", "BLCA", "BRCA", "CESC", "CHOL", "COAD", "DLBC", "ESCA", "GBM",
        "HNSC", "KICH", "KIRC", "KIRP", "LAML", "LGG", "LIHC", "LUAD", "LUSC",
        "MESO", "OV", "PAAD", "PCPG", "PRAD", "READ", "SARC", "SKCM", "STAD",
        "TGCT", "THCA", "THYM", "UCEC", "UCS", "UVM"
    ],
    "TARGET": [
        "AML", "CCSK", "NBL", "OS", "RT", "WT"
    ]
}
EXPERIMENTS = [
    "gene_expression_quantification", "isoform_expression_quantification",
    "copy_number_segment", "masked_copy_number_segment", "masked_somatic_mutation",
    "methylation_beta_value", "mirna_expression_quantification"
]

# local ontology repositories paths
ONTOLOGIES_BASEPATH = "./ontologies/";
ONTOLOGIES_REPOS = { "obofoundry": "obofoundry_objs" };
ONTOLOGIES_JSONS = { "obofoundry": "obofoundry_20180702.jsonld" }

# parameters required to correctly navigate
# the json description of an ontology repository
SEARCH_FOR_ROOT = "ontologies";
SEARCH_FOR_ID = "id";
SEARCH_FOR_ARRAY = "products";
SEARCH_FOR_TARGET = "ontology_purl";
SEARCH_FOR_EXTENSION = "owl";

# extension for the ontology serialized objects
ONTOLOGY_OBJ_EXTENSION = "zpkl";

# dictionary containing the loaded ontology objects
ONTOLOGIES_OBJS = { };

'''
cPickle utils
'''

# load an ontology serialized object
def load_zipped_pack(filepath):
    obj = None;
    with gzip.open(filepath, 'rb') as gzipfile:
        obj = cPickle.load( gzipfile );
    return obj;

# save an ontology serialized object locally
def save_zipped_pack(obj, filepath):
    with gzip.open(filepath, 'wb') as output:
        cPickle.dump( obj, output );

'''
load ontologies
'''

# browse the json description of an ontology repository
def search_for_ontology(json_filepath):
    ontologies_purls = { };
    json_data = None;
    with open(json_filepath) as json_file:
        json_data = json.load( json_file );
    if json_data != None:
        ontologies_count = len( json_data[ SEARCH_FOR_ROOT ] );
        for on in range(0, ontologies_count):
            ontology_name = json_data[ SEARCH_FOR_ROOT ][ on ][ SEARCH_FOR_ID ];
            ontology_id = ontology_name + "." + SEARCH_FOR_EXTENSION;
            if SEARCH_FOR_ARRAY in json_data[ SEARCH_FOR_ROOT ][ on ]:
                search_for_array = json_data[ SEARCH_FOR_ROOT ][ on ][ SEARCH_FOR_ARRAY ];
                for elem in search_for_array:
                    if elem[ SEARCH_FOR_ID ] == ontology_id:
                        ontologies_purls[ ontology_name ] = elem[ SEARCH_FOR_TARGET ];
                        break;
    return ontologies_purls;

def load_ontologies():
    ontologies_count = 0;
    if LOAD_ONTOLOGIES_FROM_URL:
        # load an ontology by pURL with Ontospy
        print "retrieving ontologies from pURLs";
        for repo in ONTOLOGIES_JSONS:
            repo_json_filename = ONTOLOGIES_JSONS[ repo ];
            repo_json_filepath = os.path.join( ONTOLOGIES_BASEPATH, repo_json_filename );
            ontologies_purls = search_for_ontology( repo_json_filepath );
            print "> " + repo_json_filename + " contains " + str(len(ontologies_purls)) + " ontologies";
            for ontology_id in ontologies_purls:
                print ">> " + ontologies_purls[ ontology_id ];
                model = ontospy.Ontospy( ontologies_purls[ ontology_id ] );
                obj_basepath = os.path.join( ONTOLOGIES_BASEPATH, ONTOLOGIES_REPOS[ repo ] );
                obj_filepath = os.path.join( obj_basepath, ontology_id + "." + ONTOLOGY_OBJ_EXTENSION );
                save_zipped_pack( model, obj_filepath );
                ONTOLOGIES_OBJS[ repo ][ ontology_id ] = model;
                ontologies_count += 1;
        print str(ontologies_count) + " ontologies loaded";
    else:
        # load the local ontology objects
        print "loading ontologies objects from local repository"
        for repo in ONTOLOGIES_REPOS:
            repo_objs_dir = ONTOLOGIES_REPOS[repo];
            ontology_basepath = os.path.join( ONTOLOGIES_BASEPATH, repo_objs_dir );
            if os.path.exists(ontology_basepath):
                for subdir, dirs, files in os.walk( ontology_basepath ):
                    for obj in files:
                        if obj.endswith( ONTOLOGY_OBJ_EXTENSION ):
                            obj_path = os.path.join( subdir, obj );
                            obj_name = os.path.basename( os.path.splitext( obj_path )[0] );
                            ONTOLOGIES_OBJS[ repo ][ obj_name ] = load_zipped_pack( obj_path );
                            ontologies_count += 1;
        print str(ontologies_count) + " ontologies loaded";

'''
local metadata and genomics utils
'''

def load_meta_attributes_list(program, tumor, experiment_type):
    # build target metadata directory
    meta_dir = os.path.join( os.path.join( os.path.join( METADATA_BASEPATH, program ), tumor ), experiment_type);
    meta_attributes = { };
    if os.path.exists( meta_dir ):
        for subdir, dirs, files in os.walk( meta_dir ):
            for filename in files:
                if filename.endswith( METADATA_EXTENSION ):
                    file_path = os.path.join( subdir, filename );
                    with open(file_path) as meta_file:
                        for line in meta_file:
                            line = line.strip();
                            if line != "":
                                line_split = line.split("\t");
                                meta_attribute = line_split[0];
                                meta_value = line_split[1];
                                meta_attribute_split = meta_attribute.split("__");
                                significant_meta_attribute = meta_attribute_split[-1];
                                values = [ meta_value ];
                                if significant_meta_attribute in meta_attributes:
                                    values.extend( meta_attributes[significant_meta_attribute] );
                                    values = list( set( values ) );
                                meta_attributes[significant_meta_attribute] = values;
                                # TO-DO restyle meta_attributes : split data by aliquot_uuid
    return list( set( meta_attributes ) );

def main(argv):
    '''
    implementing use case
    select aliquot_uuid from metadata where cancer = "Thoracic Cancer"
    '''
    
    '''
    # (c1=3 and c2=r) or (c4=7 and c5=1 or c6=5) and (c7=9 or c8=w)
    SEARCH_CONDITIONS = {
        "group": {
            "group": {
                "group": {
                    "entity": {
                        "op": "c1=3",
                        "hash": "eohr58"
                    },
                    "operator": {
                        "op": "and",
                        "el": "eohr58",
                        "er": "h9f3g4",
                        "hash": "ohf357"
                    },
                    "entity": {
                        "op": "c2=r",
                        "hash": "h9f3g4"
                    },
                    "hash": "bofw38"
                },
                "operator": {
                    "op": "or",
                    "el": "bofw38",
                    "er": "ch9w34",
                    "hash": "fh9b34"
                },
                "group": {
                    "group": {
                        "entity": {
                            "op": "c4=7",
                            "hash": "ifb7hf"
                        },
                        "operator": {
                            "op": "and",
                            "el": "ifb7hf",
                            "er": "h93gf4",
                            "hash": "vho3li"
                        },
                        "entity": {
                            "op": "c5=1",
                            "hash": "h93gf4"
                        },
                        "hash": "h9v35f"
                    },
                    "operator": {
                        "op": "or",
                        "el": "h9v35f",
                        "er": "f92g34",
                        "hash": "fhg924"
                    },
                    "entity": {
                        "op": "c6=5",
                        "hash": "f92g34"
                    },
                    "hash": "ch9w34"
                },
                "hash": "fh9344"
            },
            "operator": {
                "op": "and",
                "el": "fh9344",
                "er": "olb9vf",
                "hash": "ohf35f"
            },
            "group": {
                "entity": {
                    "op": "c7=9",
                    "hash": "oqg309"
                },
                "operator": {
                    "op": "or",
                    "el": "oqg309",
                    "er": "fwohr3",
                    "hash": "hfg924"
                },
                "entity": {
                    "op": "c8=w",
                    "hash": "fwohr3"
                },
                "hash": "olb9vf"
            }
        }
    }
    '''

    SELECT_CONDITIONS = [ "aliquot_uuid" ];
    SEARCH_IN_DATASET = "metadata";
    SEARCH_CONDITIONS = {
        "cancer": "Thoracic Cancer"
    }

    # search in every tumors for each program, independently from the experiment type
    metadata_attributes = [ ];
    for program in TUMORS:
        for tumor in TUMORS[program]:
            for experiment_type in EXPERIMENTS:
                metadata_attributes.extend( load_meta_attributes_list( program, tumor, experiment_type ) );

    # identify unknown attributes from the set of SELECT and WHERE
    unknown_select_attributes = [ ];
    unknown_where_attributes = [ ];
    for select_condition_attribute in SELECT_CONDITIONS:
        if select_condition_attribute not in metadata_attributes:
            unknown_select_attributes.append( select_condition_attribute );
    for where_condition_attribute in SEARCH_CONDITIONS:
        if where_condition_attribute not in metadata_attributes:
            unknown_where_attributes.append( where_condition_attribute );

    if ( len(unknown_select_attributes) + len(unknown_where_attributes) ) == 0:
        print "the dataset will not be extended";
    else:
        print "undefined attributes: " + str( ( len(unknown_select_attributes) + len(unknown_where_attributes) ) );
        print "> SELECT: " + str( unknown_select_attributes );
        print "> WHERE: " + str( unknown_where_attributes );
        print "the dataset will be extended";
        load_ontologies();
        # search for the unknown attributes in the ontologies
        # consider the WHERE unknown attributes only
        # TO-DO: SELECT unknown attributes
        for unknown_where_attribute in unknown_where_attributes:
            # stop at the first ontology that contains the WHERE unknown attribute
            # TO-DO: what if multiple ontologies contain the WHERE unknown attribute?
            candidate_ontology_id = "";
            for ontology_id in ONTOLOGIES_OBJS:
                model = ONTOLOGIES_OBJS[ ontology_id ];
                attribute_related_classes = model.getClass( unknown_where_attribute );
                if len(attribute_related_classes) > 0:
                    # consider the first class
                    # TO-DO: what if the WHERE unknown attribute is related to multiple classes in the current ontology?
                    central_attribute_class = attribute_related_classes[0];
                    in_ontology_related_attributes = central_attribute_class.parents();
                    in_ontology_related_attributes.extend( central_attribute_class.children() );
                    related_attributes_in_dataset = extract_similar_attributes( in_ontology_related_attributes, list(metadata_attributes.keys()) );
                    for related_attribute_in_dataset in related_attributes_in_dataset:
                        # search for WHERE value in the ontology
                        unknown_where_value = SEARCH_CONDITIONS[ unknown_where_attribute ];
                        value_related_classes = model.getClass( unknown_where_value );
                        if len(value_related_classes) > 0:
                            # consider the first class
                            # TO-DO: what if the WHERE unknown value is related to multiple classes in the current ontology?
                            central_value_class = attribute_related_classes[0];
                            in_ontology_related_values = central_value_class.parents();
                            in_ontology_related_values.extend( central_value_class.children() );
                            if related_attribute_in_dataset in in_ontology_related_values:
                                # extend dataset temporarily and use this temp version in the next iterations
                                candidate_ontology_id = ontology_id;
                                break;
                    break;

if __name__ == '__main__':
    main(sys.argv[1:])
