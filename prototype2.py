import os, json, gzip, msgpack
import ontospy

# set this parameter to False if the local repository
# already contains the ontology serialized objects
LOAD_FROM_URL = True;

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
ONTOLOGY_OBJ_EXTENSION = "obj";

# dictionary containing the loaded ontology objects
ONTOLOGIES_OBJS = { };

# load an ontology serialized object
def load_zipped_pack(filepath):
    obj = None;
    with gzip.open(filepath, 'rb') as gzipfile:
        data = gzipfile.read();
    obj = msgpack.unpackb(data, raw=False);
    return obj;

# save an ontology serialized object locally
def save_zipped_pack(obj, filepath):
    with gzip.open(filepath, 'wb') as output:
        output.write( msgpack.packb( obj, use_bin_type=True ) );

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

ontologies_count = 0;
if LOAD_FROM_URL:
    # load an ontology by pURL with Ontospy
    print "retrieving ontologies from pURLs";
    for repo in ONTOLOGIES_JSONS:
        repo_json_filename = ONTOLOGIES_JSONS[ repo ];
        repo_json_filepath = os.path.join( ONTOLOGIES_BASEPATH, repo_json_filename );
        ontologies_purls = search_for_ontology( repo_json_filepath );
        print "> " + repo_json_filename + " contains " + str(len(ontologies_purls)) + " ontologies";
        for ontology_id in ontologies_purls:
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
