#!/usr/bin/python3.5
# student: J.F.P. (Richard) Scholtens
# studentnr.: s2956586
# datum: 10/10/2019


from SPARQLWrapper import SPARQLWrapper, JSON
import json
import pickle
import re
import requests


def retrieve_info(query, subject, check=False, splitter=False):
    """Returns the values of a given query."""

    dic = {}
    sparql = SPARQLWrapper("http://dbpedia.org/sparql")
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()

    if check:
        print("### CHECK IS TRUE: ",results)

    for result in results["results"]["bindings"]:
        if splitter:
            dic[result[subject]["value"].rsplit('/', 1)[-1]] = result[subject]["value"]
        else:
            dic[result[subject]["value"]] = result[subject]["value"]

    return dic


def jaccard_index(set1, set2):
    """Computes the Jaccard index between two sets
    of characters."""
    return len(set1 & set2) / len(set1.union(set2))


def count_unicode(string):
    """Counts the accents in a string."""
    c = 0
    for char in string:
        if not re.match('^[a-zA-Z_]+$', char):
            c += 1
    return c


def get_entities(json_file):
    """Returns entities from a json file."""
    with open(json_file, "r") as data:
        datastore = json.load(data)
        return datastore


def remove_part(string, ch, count): 
    """Removes the last part of a string given a charachter
    and how many times it may occur. Returns the first part
    of a string."""
    occ = 0
    new_string = ""
    for i in range(len(string)): 
        if (string[i] == ch): 
            occ += 1
        if (occ == count): 
            break
        new_string +=  string[i]
    if new_string[-1] ==  "_":
        new_string =  new_string[:-1]
    return new_string



def retrieve_resource(dic):
    """Returns all resources in a dictionary for the given keys from
    the input dictionary."""
    sec_dic = {}
    for k, v in dic.items():
        k = k.strip()
        query = """SELECT ?resource WHERE { ?resource rdfs:label "%s"@en}""" % k
        new_k = remove_part(k, "(", 1)
        new_k = new_k.strip("\t")
        new_k = new_k.replace(" ", "_")
        try:
            sparql_dic = retrieve_info(query, "resource")

            for value in sparql_dic.values():

                if new_k == value.rsplit('/', 1)[-1]:

                    sec_dic[new_k] = value
                    break
        except:
            pass
    return sec_dic


def correct_names(data, predicate, query, enrich_teams, count, key):
    """Checks if name labels are similar enough and if not which name
    holds the highest number accents. Returns updated dictionary."""
    dic = retrieve_info(query, "value")
    if len(dic) >= 1:
        for value in dic.values():
            if jaccard_index(set(data), set(value)) < 0.76 and count_unicode(data) <= count_unicode(value):
                enrich_teams[key][predicate] = value
                count += 1
                return enrich_teams, count
            else:
                enrich_teams[key][predicate] = data
                return enrich_teams, count
    else:
        enrich_teams[key][predicate] = data
        return enrich_teams, count


def add_info(data, predicate, dic, key, count, year=False):
    """Adds info to dictionary but also checks if year must 
    be included. Returns updated dictionary."""
    if year and data:
        dic[key][predicate] = data + " (" + year + ")"
        count += 1
    else:
        dic[key][predicate] = data
        count += 1
    return dic, count



def enrich_URI(data, predicate, query, enrich_teams, count, key, count2, check=False):
    """Checks if there is an URI for the data and if so tries to add this as an HTML
    code. Returns updated dictionary."""
    enrich_dic = retrieve_info(query, "value")
    if len(enrich_dic) >= 1:
        for value in enrich_dic.values():

            new_value = value.rsplit('/', 1)[-1].replace("_", " ")
            if check:
                if data in new_value:
                    enrich_teams[key][predicate] = "<a href='%s'>" % value + new_value + "</a>"
                    count += 1
                    return enrich_teams, count, count2
                else:
                    enrich_teams[key][predicate] = data
                    count2 += 1
                    return enrich_teams, count, count2
            else:
                enrich_teams[key][predicate] = "<a href='%s'>" % value + new_value + "</a>"
                count += 1
                return enrich_teams, count, count2
                
        return enrich_teams, count, count2
    else:
        enrich_teams[key][predicate] = data
        count2 += 1
        return enrich_teams, count, count2


def enrich_data(data, predicate, query, enrich_rt, count, key, count2):
    """Adds unprovided data to dictionary."""
    enrich_dic = retrieve_info(query, "value")
    if len(enrich_dic) >= 1:
        for value in enrich_dic.values():
            enrich_rt[key][predicate] = value
            count += 1
            return enrich_rt, count, count2 
    else:
        enrich_rt[key][predicate] = data
        count2 += 1
        return enrich_rt, count, count2 


def main():
    riders_dic = get_entities('riders.json')
    rider_rdic = retrieve_resource(riders_dic)

    teams_dic = get_entities('t_teams.json')
    team_rdic = retrieve_resource(teams_dic)

    not_found = set()
    not_found2 = set()
    enrich_riders = {}
    enrich_teams = {}

    added_ucirank = 0
    added_birthPlace = 0
    added_birthDate = 0
    added_weight = 0
    added_height = 0
    added_ridertype = 0
    added_givenname = 0
    added_surname = 0
    added_proteam = 0
    added_bike = 0
    added_status = 0
    added_ucicode = 0
    added_url = 0
    nf_registered = 0


    enrich_weight = 0
    enrich_height = 0
    enrich_nationality = 0
    enrich_birthPlace = 0
    enrich_proteam = 0
    enrich_givenName = 0
    enrich_surname = 0
    enrich_ridertype = 0
    enrich_bike = 0
    enrich_registered = 0

    nf_ucirank = 0
    nf_birthDate = 0
    nf_weight = 0
    nf_height = 0
    nf_ridertype = 0
    nf_givenName = 0
    nf_surname = 0
    nf_proteam = 0
    nf_nationality = 0
    nf_birthPlace = 0
    nf_bike = 0
    nf_status = 0
    nf_ucicode = 0
    nf_url = 0
    nf_registered = 0
    nf_ridertype = 0


    for k, v in riders_dic.items():
        k = k.strip()
        old_k = k
        enrich_riders[old_k] = {}

        k = k.replace(" ", "_")

        # CHECK IF RIDERS CAN BE ENRICHED
        if k in rider_rdic.keys():
            resource = rider_rdic[k]

            for predicate, data in v.items():
                enrich_query = """SELECT ?value WHERE { <%s> %s ?value }""" % (resource, predicate)


                if predicate == "dbo:proteam":
                    predicate = "dbp:proteam"
                if predicate == "uci_rank":
                        predicate = "dbp:uciRank"


                # CHECK IF DATA ALREADY HAS BEEN PROVIDED
                if data:

                    if data == str(data):
                        data = data.strip()
                        data = data.replace("\t", "")
                        data2 = data.replace(" ", "_")

                    # ADDING PROCYCLINGSTATS DATA
                    ################# 

                    ### UCI RANK
                    if predicate == "dbp:uciRank":
                        enrich_riders, added_ucirank = add_info(data, predicate, enrich_riders, old_k, added_ucirank)

                    ### BIRTH DATE
                    elif predicate == "dbo:birthDate":
                        enrich_riders, added_birthDate = add_info(data, predicate, enrich_riders, old_k, added_birthDate)

                    ### WEIGHT
                    elif predicate == "dbo:weight":
                        enrich_riders, added_weight = add_info(data, predicate, enrich_riders, old_k, added_weight)

                    ### HEIGHT
                    elif predicate == "dbo:height":
                        enrich_riders, added_height = add_info(data, predicate, enrich_riders, old_k, added_height)


                    ### RIDER TYPE
                    elif predicate == "dbp:ridertype":
                        enrich_riders, added_ridertype = add_info(data, predicate, enrich_riders, old_k, added_ridertype)



                    # CHECKING AND CORRECTING NAMES
                    ################# 
                    
                    ### GIVEN NAME
                    elif predicate == "foaf:givenName":

                        enrich_riders, enrich_givenName = correct_names(data, predicate, enrich_query, enrich_riders, enrich_givenName, old_k)


                    elif predicate == "foaf:surname":
                        enrich_riders, enrich_surname = correct_names(data, predicate, enrich_query, enrich_riders, enrich_surname, old_k)


                    # CHECKING AND ENRICHING DATA
                    ##################

                    ### NATIONALITY
                    elif predicate == "dbo:nationality":

                        enrich_riders[old_k][predicate] = "<a href='http://dbpedia.org/resource/%s'>" % data2 + data + "</a>"
                        enrich_nationality += 1

                    ### BIRTH PLACE
                    elif predicate == "dbo:birthPlace":
                        enrich_riders[old_k][predicate] = "<a href='http://dbpedia.org/resource/%s'>" % data2 + data + "</a>"
                        enrich_birthPlace += 1

                    ### PRO TEAM
                    elif predicate == "dbp:proteam":

                        enrich_riders, enrich_proteam, added_proteam = enrich_URI(data, predicate, enrich_query, enrich_riders, enrich_proteam, old_k, added_proteam)


                # IF DATA NOT PROVIDED TRY TO RETRIEVE ENRICHED DATA
                ###############

                ### UCI RANK
                elif predicate == "dbp:uciRank":
                    enrich_riders, added_ucirank = add_info(data, predicate, enrich_riders, old_k, added_ucirank)

                ### UCI RANK
                elif predicate == "dbo:birthPlace":
                    enrich_riders, added_birthPlace = add_info(data, predicate, enrich_riders, old_k, added_birthPlace)


                ### RIDER TYPE
                elif predicate == "dbp:ridertype":
                    enrich_riders, enrich_ridertype, nf_ridertype = enrich_data(data, predicate, enrich_query, enrich_riders, enrich_ridertype, old_k, nf_ridertype)

                ### BIRTH PLACE
                elif predicate == "dbo:birthPlace":
                    enrich_riders, enrich_birthPlace, added_birthPlace = enrich_URI(data, predicate, enrich_query, enrich_riders, enrich_birthPlace, old_k, added_birthPlace)

                ### PRO TEAM
                elif predicate == "dbp:proteam":
                    enrich_riders, enrich_proteam, added_proteam = enrich_URI(data, predicate, enrich_query, enrich_riders, enrich_proteam, old_k, added_proteam)

                ### ADD WEIGHT
                elif predicate == "dbo:weight":
                    enrich_dic = retrieve_info(enrich_query, "value")
                    if len(enrich_dic) >= 1:
                        for value in enrich_dic.values():
                            enrich_riders[old_k][predicate] = round((float(value) / 1000), 1)
                            enrich_weight += 1
                            break
                    else:
                        enrich_riders[old_k][predicate] = data

                ### ADD HEIGHT
                elif predicate == "dbo:height":
                     enrich_riders, enrich_height, nf_height = enrich_data(data, predicate, enrich_query, enrich_riders, enrich_height, old_k, nf_height)

        # RIDER DATA COULD NOT BE FOUND IN DBPEDIA
        else:
            not_found.add(k)
            for predicate, data in v.items():

                if predicate == "uci_rank":
                    predicate = "dbp:uciRank"

                # CHECK IF DATA ALREADY HAS BEEN PROVIDED
                if data:
                    if data == str(data):
                        data = data.strip()
                        data = data.replace("\t", "")
                        data2 = data.replace(" ", "_")

                    ### UCI RANK
                    if predicate == "dbp:uciRank":
                        enrich_riders, added_ucirank = add_info(data, predicate, enrich_riders, old_k, added_ucirank)

                    ### BIRTH DATE
                    elif predicate == "dbo:birthDate":
                        enrich_riders, added_birthDate = add_info(data, predicate, enrich_riders, old_k, added_birthDate)

                    ### WEIGHT
                    elif predicate == "dbo:weight":
                        enrich_riders, added_weight = add_info(data, predicate, enrich_riders, old_k, added_weight)

                    ### HEIGHT
                    elif predicate == "dbo:height":
                        enrich_riders, added_height = add_info(data, predicate, enrich_riders, old_k, added_height)


                    ### CYCLIST GENRE
                    elif predicate == "dbp:ridertype":
                        enrich_riders, added_ridertype = add_info(data, predicate, enrich_riders, old_k, added_ridertype)

                    ### GIVEN NAME
                    elif predicate == "foaf:givenName":
                        enrich_riders, added_givenname = add_info(data, predicate, enrich_riders, old_k, added_givenname)


                    ### SURNAME
                    elif predicate == "foaf:surname":
                        enrich_riders, added_surname = add_info(data, predicate, enrich_riders, old_k, added_surname)


                     ### PROTEAM
                    elif predicate == "dbp:proteam":
                        enrich_riders, added_proteam = add_info(data, predicate, enrich_riders, old_k, added_proteam)


                    ### NATIONALITY
                    elif predicate == "dbo:nationality":
                        enrich_riders[old_k][predicate] = "<a href='http://dbpedia.org/resource/%s'>" % data2 + data + "</a>"
                        enrich_nationality += 1

                    ### BIRTHPLACE
                    elif predicate == "dbo:birthPlace":
                        enrich_riders[old_k][predicate] = "<a href='http://dbpedia.org/resource/%s'>" % data2 + data + "</a>"
                        enrich_birthPlace += 1


                ### UCI RANK
                elif predicate == "dbp:uciRank":
                    enrich_riders, nf_ucirank = add_info(data, predicate, enrich_riders, old_k, nf_ucirank)

                ### BIRTH DATE
                elif predicate == "dbo:birthDate":
                    enrich_riders, nf_birthDate = add_info(data, predicate, enrich_riders, old_k, nf_birthDate)

                ### WEIGHT
                elif predicate == "dbo:weight":
                    enrich_riders, nf_weight = add_info(data, predicate, enrich_riders, old_k, nf_weight)

                ### HEIGHT
                elif predicate == "dbo:height":
                    enrich_riders, nf_height = add_info(data, predicate, enrich_riders, old_k, nf_height)


                ### CYCLIST GENRE
                elif predicate == "dbp:ridertype":
                    enrich_riders, nf_ridertype = add_info(data, predicate, enrich_riders, old_k, nf_ridertype)

                ### GIVEN NAME
                elif predicate == "foaf:givenName":
                    enrich_riders, nf_givenname = add_info(data, predicate, enrich_riders, old_k, nf_givenname)


                ### SURNAME
                elif predicate == "foaf:surname":
                    enrich_riders, nf_surname = add_info(data, predicate, enrich_riders, old_k, nf_surname)


                ### PROTEAM
                elif predicate == "dbp:proteam":
                    enrich_riders, nf_proteam = add_info(data, predicate, enrich_riders, old_k, nf_proteam)


                ### NATIONALITY
                elif predicate == "dbo:nationality":
                    enrich_riders, nf_nationality = add_info(data, predicate, enrich_riders, old_k, nf_nationality)

                ### BIRTHPLACE
                elif predicate == "dbo:birthPlace":
                    enrich_riders, nf_birthPlace = add_info(data, predicate, enrich_riders, old_k, nf_birthPlace)

                resource = None
    
    found = len(riders_dic) - len(not_found)
    print("### RIDERS")
    print("Total riders:\t\t", len(riders_dic))
    print("Not found riders:\t", len(not_found))
    print("Found riders:\t\t", found)


    print("\n### DATA ENRICHED WITH DBPEDIA\n")


    print("MISSING DATA ADDED")
    print("Weight:\t\t\t", enrich_weight)
    print("Height:\t\t\t", enrich_height)
    print("Ridertype:\t\t", enrich_ridertype)
    
    print("\nCORRECTED DATA ADDED")
    print("Given name:\t\t", enrich_givenName)
    print("Surname:\t\t", enrich_surname)

    print("\nURI DATA ADDED")
    print("Nationality:\t\t", enrich_nationality)
    print("Birth place:\t\t", enrich_birthPlace)
    print("Pro team:\t\t", enrich_proteam)

    print("\n### DATA ADDED FROM PRO CYCLING STATS ENRICHED DATA EXCLUDED\n")
    print("Birth dates:\t\t", added_birthDate)
    print("Birth places:\t\t", added_birthPlace)
    print("Height:\t\t\t", added_height)
    print("Pro team:\t\t", added_proteam)
    print("Rider type:\t\t", added_ridertype)
    print("UCI Ranks:\t\t", added_ucirank)
    print("Weight:\t\t\t", added_weight)


    print("\n### DATA WAS NOT FOUND\n")
    print("Birth dates:\t\t", nf_birthDate)
    print("Birth place:\t\t", nf_birthPlace)
    print("Given name:\t\t", nf_givenName)
    print("Height:\t\t\t", nf_height)
    print("Nationality:\t\t", nf_nationality)
    print("Pro team:\t\t", nf_proteam)
    print("Rider type:\t\t", nf_ridertype)
    print("Surname:\t\t", nf_surname)    
    print("UCI Ranks:\t\t", nf_ucirank)
    print("Weight:\t\t\t", nf_weight)

    with open("enriched_riders.json", "w") as write_file:
        json.dump(enrich_riders, write_file)

    for k, v in teams_dic.items():
        k = k.strip()
        old_k = k
        enrich_teams[old_k] = {}

        k = k.replace(" ", "_")

        # CHECK IF TEAMS CAN BE ENRICHED
        if k in team_rdic.keys():
            registration = False
            resource = team_rdic[k]

            registered_query = """SELECT ?value WHERE { <%s> %s ?value }""" % (resource, "dbp:registered")
            enrich_teams, enrich_registered, nf_registered = enrich_URI(None, "dbp:registered", registered_query, enrich_teams, enrich_registered, old_k, nf_registered)
            
            for predicate, data in v.items():

                if predicate == "url":
                    predicate = "foaf:PCS"

                enrich_query = """SELECT ?value WHERE { <%s> %s ?value }""" % (resource, predicate)

                # CHECK IF DATA ALREADY HAS BEEN PROVIDED
                if data:

                    if data == str(data):
                        data = data.strip()
                        data = data.replace("\t", "")
                        data2 = data.replace(" ", "_")

                    # ADDING PROCYCLINGSTATS DATA
                    ################# 

                    ### STATUS
                    if predicate == "dbo:status":
                        enrich_teams, added_status = add_info(data, predicate, enrich_teams, old_k, added_status, "2019")

                    ### UCI CODE
                    elif predicate == "dbo:uciCode":
                        enrich_teams, added_ucicode = add_info(data, predicate, enrich_teams, old_k, added_ucicode)

                    ### PCS URL
                    elif predicate == "foaf:PCS":
                        enrich_teams, added_url = add_info(data, predicate, enrich_teams, old_k, added_url)


                    # CHECKING AND ENRICHING DATA
                    ##################

                    ### BICYCLES
                    elif predicate == "dbp:bicycles":
                        enrich_teams, enrich_bike, added_bike = enrich_URI(data, predicate, enrich_query, enrich_teams, enrich_bike, old_k, added_bike, True)


                ### STATUS
                elif predicate == "dbo:status":
                    enrich_teams, added_status = add_info(data, predicate, enrich_teams, old_k, added_status, "2019")

                ### UCI CODE
                elif predicate == "dbo:uciCode":
                    enrich_teams, added_ucicode = add_info(data, predicate, enrich_teams, old_k, added_ucicode)

                ### PCS URL
                elif predicate == "foaf:PCS":
                    enrich_teams, added_url = add_info(data, predicate, enrich_teams, old_k, added_url)

                # IF DATA NOT PROVIDED TRY TO RETRIEVE ENRICHED DATA
                ### BICYCLES
                elif predicate == "dbp:bicycles":

                    enrich_teams, enrich_bike, added_bike = enrich_URI(data, predicate, enrich_query, enrich_teams, enrich_bike, old_k, added_bike)


        # TEAM DATA COULD NOT BE FOUND IN DBPEDIA
        else:
            not_found2.add(k)
            enrich_teams, nf_registered = add_info(None, "dbp:registered", enrich_teams, old_k, nf_registered)
 
            # CHECK IF DATA ALREADY HAS BEEN PROVIDED
            for predicate, data in v.items():

                if predicate == "url":
                    predicate = "foaf:PCS"

                if data:
                    if data == str(data):
                        data = data.strip()
                        data = data.replace("\t", "")
                        data2 = data.replace(" ", "_")

                    # ADDING PROCYCLINGSTATS DATA
                    ################# 

                    ### STATUS
                    if predicate == "dbo:status":
                        enrich_teams, added_status = add_info(data, predicate, enrich_teams, old_k, added_status, "2019")

                    ### UCI CODE
                    elif predicate == "dbo:uciCode":
                        enrich_teams, added_ucicode = add_info(data, predicate, enrich_teams, old_k, added_ucicode)

                    ### PCS URL
                    elif predicate == "foaf:PCS":
                        enrich_teams, added_url = add_info(data, predicate, enrich_teams, old_k, added_url)

                    ### BICYCLES
                    elif predicate == "dbp:bicycles":
                        enrich_teams, added_bike = add_info(data, predicate, enrich_teams, old_k, added_bike)

                ### STATUS
                elif predicate == "dbo:status":
                    enrich_teams, nf_status = add_info(data, predicate, enrich_teams, old_k, nf_status, "2019")

                ### UCI CODE
                elif predicate == "dbo:uciCode":
                    enrich_teams, nf_ucicode = add_info(data, predicate, enrich_teams, old_k, nf_ucicode)

                ### PCS URL
                elif predicate == "foaf:PCS":
                    enrich_teams, added_url = add_info(data, predicate, enrich_teams, old_k, added_url)

                ### BICYCLES
                elif predicate == "dbp:bicycles":
                    enrich_teams, nf_bike = add_info(data, predicate, enrich_teams, old_k, nf_bike)

                resource = None

    found2 = len(teams_dic) - len(not_found2)

    print("\n\n### Teams")
    print("Total teams:\t\t", len(teams_dic))
    print("Not found teams:\t", len(not_found2))
    print("Found teams:\t\t", found2)


    print("\n### DATA ENRICHED WITH DBPEDIA\n")

    print("MISSING DATA ADDED")

    print("\nURI DATA ADDED")
    print("Bikes:\t\t\t", enrich_bike)
    print("Registered:\t\t", enrich_registered)

    print("\n### DATA ADDED FROM PRO CYCLING STATS ENRICHED DATA EXCLUDED\n")
    print("Bicycles:\t\t", added_bike)
    print("PCS URL:\t\t", added_url)
    print("Status:\t\t\t", added_status)
    print("UCI Code:\t\t", added_ucicode)

    print("\n### DATA WAS NOT FOUND\n")
    print("Bicycles:\t\t", nf_bike)
    print("PCS URL:\t\t", nf_url)
    print("Registered:\t\t", nf_registered)
    print("Status:\t\t\t", nf_status)
    print("UCI Code:\t\t", nf_ucicode)

    with open("enriched_teams.json", "w") as write_file:
        json.dump(enrich_teams, write_file)

if __name__ == '__main__':
    main()
