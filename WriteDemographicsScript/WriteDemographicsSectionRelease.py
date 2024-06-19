# source of format was gonna be mostly from https://en.wikipedia.org/w/index.php?title=New_London,_Connecticut&oldid=1226652069#2020_census, but https://en.wikipedia.org/w/index.php?title=Stephens_City,_Virginia&oldid=1222587193#Demographics was also very useful, if not the most used (each section has a corresponding link to where the format came from)
# which is one where I edited the 2010 version to update with
# all the information I could find for the 2020 census.
# vaguely updating it to make it sound better to me

# Random stuff that seems pretty useful/good examples or whatever

# this one looks pretty good, for an example of mixed data
# https://en.wikipedia.org/wiki/Minneapolis#Census_and_estimates

# TODO: https://en.wikipedia.org/w/index.php?title=Albany,_New_York&oldid=1227840151#2020_census
# has a pretty good note that I might want to steal (note r)

# TODO: future project could be cool https://cde.ucr.cjis.gov/LATEST/webapp/#/pages/docApi

# for more information, I found the first page of
# https://www.census.gov/content/dam/Census/library/publications/2020/acs/acs_api_handbook_2020_ch02.pdf
# to be very helpful for understanding all the bits of the query, and of course there's
# easier to find guides for the API and good examples

import requests
from datetime import date
# I looked into using the census module and it was too complicated
# to figure out. Using it at this point would prolly get rid of 10
# lines, and I'd understand what I was doing a lot less, so I'm glad
# that I didn't use it

class DataType:
    # for instance, demographics data about
    # number of households would be DataType(DP02_0001E, profile)
    # while number of families is subject data and would be
    # DataType("S1101_C01_003E", "subject")
    def __init__(self, name_of_data, data_location):
        self.NAME = name_of_data
        self.LOCATION = data_location

class CensusGetter():
    def __init__(self, API_Key):
        # if you don't have an api key
        # get one here https://api.census.gov/data/key_signup.html,
        # it only took me like 5 minutes tops to do
        self.API_Key = API_Key
        self.location_info = {}
        # we'll use acs1 if we're able to (only towns which have around 65K+ folks
        # have acs1. Otherwise, they average it across the past 5 years)
        self.use_acs1 = False
        # schedule for 2023 release is here:
        # https://www.census.gov/programs-surveys/acs/news/data-releases/2023/release-schedule.html
        # ACS5 releases ~December the subsequent year
        self.MOST_RECENT_ACS5_DATE = 2022
        # and ACS1 releases ~September the subsequent year
        self.MOST_RECENT_ACS1_DATE = 2022
        # I thiink it releases around September of the same year
        self.MOST_RECENT_GAZETTEER_DATE = 2023

    # paste in the row of the data table that you want
    # from https://www.census.gov/library/reference/code-lists/ansi.html
    # paste in the one from the relevant place table,
    # which for New London city, Connecticut would be found
    # here https://www2.census.gov/geo/docs/reference/codes2020/place/st09_ct_place2020.txt
    # and would be like this:
    # CT|09|52280|02378286|New London city|INCORPORATED PLACE|C1|A|New London County
    def set_place(self, place_info_paste):
        the_split = place_info_paste.split("|")
        # these are the codes, 09 and 52280 in the example above
        self.location_info = {"state" : the_split[1], "place" : the_split[2]}
        # spelled out version, New London city from above
        self.place_english_name = the_split[4]
        # CT above
        self.postal_code = the_split[0]
        # check if we're able to use acs1 here
        # if getting the name from acs1 is non-empty, then acs1
        # data exists. If it is empty, then it doesn't exist
        self.use_acs1 = (self.get_data_from_table("acs/acs1", self.MOST_RECENT_ACS1_DATE, "NAME").text != '')

    # return the link to the data table that the information can be found
    def get_link_for_param_acs(self, param_name):
        # this is where the gazetteer area data can be found, so if we're looking at land area, return
        # this data immediately
        if param_name in ["land_area"]:
            return "https://www.census.gov/geographies/reference-files/time-series/geo/gazetteer-files.html"
        # otherwise, we're citing the normal census
        first_part = "https://data.census.gov/table/"
        # first part of link, found by just looking at various data tables
        if self.params[param_name].LOCATION == "":
            first_part += "ACSDT"
        elif self.params[param_name].LOCATION == "profile":
            first_part += "ACSDP"
        elif self.params[param_name].LOCATION == "subject":
            first_part += "ACSST"
        else:
            # good error message :-)
            print("UNRECOGNIZED LOCATION")
            print("literally, what is: ", self.params[param_name].LOCATION)
            print("of param ", param_name)
            print("???????????")
            return "uh oh"
        if self.use_acs1:
            first_part += "1Y"
        else:
            first_part += "5Y"

        # 160XX00US I thiiink indicates that we're looking at a city within
        # a town rather than a county (050) or a state (040). I'm not positive
        # about this, and might update the script to also be able to handle
        # counties + states later (and ditto for CDPs)
        date_to_use = self.MOST_RECENT_ACS1_DATE if self.use_acs1 else self.MOST_RECENT_ACS5_DATE
        return  first_part +\
                str(date_to_use) + "." +\
                self.get_data_table_of_param(param_name) + "?g=160XX00US" +\
                self.location_info["state"] + self.location_info["place"]

    # returns the full reference for a specific param with a name
    def get_named_reference_for_param_acs(self, param_name):
        # special case when we're referencing Gazetteer data instead of
        # census proper data
        if param_name in ["land_area"]:
            # not including access-date since I'm not querying the data in real time,
            # rather looking at a static file
            # QUESTION: should this include the actual land area figure? (i.e. say we
            # use "152 square miles from yada yada" or as is)
            # QUESTION: should this be a note?
            return "<ref name=Gaz" + str(self.MOST_RECENT_GAZETTEER_DATE) + ">" +\
                    "To calculate density we use the land area figure from the places file in " +\
                    "{{cite web| url=" + self.get_link_for_param_acs(param_name) +" | title = The "+\
                    str(self.MOST_RECENT_GAZETTEER_DATE) + " U.S. Gazetteer Files}}</ref>"
        # the ref_name is the data table the info is contained in
        ref_name = self.get_data_table_of_param(param_name)
        return "<ref name=" + ref_name +\
                ">{{cite web|url=" + self.get_link_for_param_acs(param_name) + "| title= "\
                    + self.get_title_for_acs(param_name, ref_name) +\
                    " | access-date = " + str(date.today()) + " | publisher = " +\
                    "[[United States Census Bureau]]" + "}}</ref>"

    # breaking out title getter into seperate function to make it more
    # modular. Including unused param_name just in case it warrants
    # future usage
    def get_title_for_acs(self, param_name, ref_name):
        if self.use_acs1:
            date_source_part = str(self.MOST_RECENT_ACS1_DATE) + " American Community Survey 1 Year Estimate: "
        else:
            date_source_part = str(self.MOST_RECENT_ACS5_DATE) + " American Community Survey 5 Year Estimate: "

        return date_source_part + self.table_names[ref_name] +\
                " for " + self.place_english_name + ", " + self.postal_code

    def get_data_table_of_param(self, param_name):
        # the split[0] gets which data table it is by taking everything
        # before the first underscore.
        return self.params[param_name].NAME.split("_")[0]

    # get a specific entry in a data_table (name_of_data is the location in the data table with the
    # underscores and the numbers), data_source is whether
    # it's subject, profile, or "" (B data) and the extension (acs/acs1 or acs/acs5)
    # data_year is what year's data we're looking at.
    def get_data_from_table(self, data_source, data_year, name_of_data):
        # sorry I don't like string formatting :-)
        # this is sorta just, right? I hope it'll also work for Census data
        query = "https://api.census.gov/data/" + str(data_year) + "/" + data_source +\
                    "?get=" + name_of_data + "&for=place:" + self.location_info["place"] +\
                    "&in=state:" + self.location_info["state"] + "&key=" + self.API_Key

        return requests.get(query)

    # initialize all of the long names of the params and also the location
    # that they can be found
    def init_acs_params(self):
        # the E at the end represents getting the Estimated amount
        # PE would get percent of total
        # and M and PM would get the respective margins of error (presumeably
        # 95% confidence intervals??)
        self.params = {
            "num_housing_units" : DataType("B25001_001E", ""),
            "num_families" : DataType("S1101_C01_003E", "subject"),
            "average_family_size" : DataType("DP02_0017E", "profile"),
            "average_household_size" : DataType("DP02_0016E", "profile"),
            "total_population" : DataType("DP05_0001E", "profile"),
            "male_population" : DataType("DP05_0002E", "profile"),
            "female_population" : DataType("DP05_0003E", "profile"),
            "under_18_population" : DataType("DP05_0019E", "profile"),
            "males_per_hundred_females" : DataType("DP05_0004E", "profile"),
            # using median age since that's where we reference age (it doesn't super
            # matter in the scheme of things, but it cuts down on one citation sometimes)
            "median_age" : DataType("S0101_C01_032E", "subject"),
            "num_households" : DataType("DP02_0001E", "profile"),
            # minors meaning younger than 18, seniors meaning 65 and older
            "num_households_with_minors" : DataType("DP02_0014E", "profile"),
            "num_households_with_seniors" : DataType("DP02_0015E", "profile"),
            "num_households_married" : DataType("DP02_0002E", "profile"),
            "num_households_cohabitating" : DataType("DP02_0004E", "profile"),
            "num_households_male_sans_partner" : DataType("DP02_0006E", "profile"),
            # i.e. single dad
            "num_households_male_sans_partner_w_children" : DataType("DP02_0007E", "profile"),
            "num_households_female_sans_partner" : DataType("DP02_0010E", "profile"),
            # i.e. single mom
            "num_households_female_sans_partner_w_children" : DataType("DP02_0011E", "profile"),
            "median_income_household_overall" : DataType("S1901_C01_012E", "subject"),
            "median_income_household_family" : DataType("S1901_C02_012E", "subject"),
            "median_income_household_non_family" : DataType("S1901_C04_012E", "subject"),
            # race
            "num_one_race" : DataType("DP05_0034E", "profile"),
            "num_two_or_more_race" : DataType("DP05_0035E", "profile"),
            "num_solely_white" : DataType("DP05_0037E", "profile"),
            "num_solely_black_or_african_american" : DataType("DP05_0038E", "profile"),
            "num_solely_american_indian_or_alaska_native" : DataType("DP05_0039E", "profile"),
            "num_solely_asian" : DataType("DP05_0044E", "profile"),
            "num_solely_native_hawaiian_or_other_pacific_islander" : DataType("DP05_0052E", "profile"),
            "num_solely_some_other_race" : DataType("DP05_0057E", "profile"),
            # number of people who identify at all with race (so it double (or more)
            # counts those who identify with more than one race)
            # watch out, these updated in 2022 from 2021, so they might update
            # again??
            "num_white" : DataType("DP05_0066E", "profile"),
            "num_black_or_african_american" : DataType("DP05_0067E", "profile"),
            "num_american_indian_or_alaska_native" : DataType("DP05_0068E", "profile"),
            "num_asian" : DataType("DP05_0069E", "profile"),
            "num_native_hawaiian_or_other_pacific_islander" : DataType("DP05_0070E", "profile"),
            "num_some_other_race" : DataType("DP05_0071E", "profile"),
            # hispanic folks! They're seperated from race since they comprise
            # an ethnicity
            "num_hispanic_or_latino" : DataType("DP05_0073E", "profile"),
            # poverty status, dealing with raw numbers instead of their percentages
            # since that gives strictly more flexibility
            "num_with_determined_poverty_status" : DataType("S1701_C01_001E", "subject"),
            "num_below_poverty_level" : DataType("S1701_C02_001E", "subject"),
            "num_minors_status_determined" : DataType("S1701_C01_002E", "subject"),
            "num_minors_below_poverty_level" : DataType("S1701_C02_002E", "subject"),
            "num_seniors_status_determined" : DataType("S1701_C01_010E", "subject"),
            "num_seniors_below_poverty_level" : DataType("S1701_C02_010E", "subject"),
            # including gender since that could be interesting if they're disparate
            "num_male_status_determined" : DataType("S1701_C01_011E", "subject"),
            "num_male_below_poverty_level" : DataType("S1701_C02_011E", "subject"),
            "num_female_status_determined" : DataType("S1701_C01_012E", "subject"),
            "num_female_below_poverty_level" : DataType("S1701_C02_012E", "subject"),
            # age jazz!
            "num_under_18" : DataType("S0101_C01_022E", "subject"),
            "num_18_to_24" : DataType("S0101_C01_023E", "subject"),
            "num_25_to_29" : DataType("S0101_C01_007E", "subject"),
            "num_30_to_34" : DataType("S0101_C01_008E", "subject"),
            "num_35_to_39" : DataType("S0101_C01_009E", "subject"),
            "num_40_to_44" : DataType("S0101_C01_010E", "subject"),
            "num_45_to_49" : DataType("S0101_C01_011E", "subject"),
            "num_50_to_54" : DataType("S0101_C01_012E", "subject"),
            "num_55_to_59" : DataType("S0101_C01_013E", "subject"),
            "num_60_to_64" : DataType("S0101_C01_014E", "subject"),
            "num_65_and_over" : DataType("S0101_C01_030E", "subject"),
            "per_capita_income" : DataType("S1902_C03_019E", "subject"),
            # ancestry time!!
            "num_american" : DataType("DP02_0125E", "profile"),
            "num_arab" : DataType("DP02_0126E", "profile"),
            "num_czech" : DataType("DP02_0127E", "profile"),
            "num_danish" : DataType("DP02_0128E", "profile"),
            "num_dutch" : DataType("DP02_0129E", "profile"),
            "num_english" : DataType("DP02_0130E", "profile"),
            "num_french_(except_basque)" : DataType("DP02_0131E", "profile"),
            "num_french_canadian" : DataType("DP02_0132E", "profile"),
            "num_german" : DataType("DP02_0133E", "profile"),
            "num_greek" : DataType("DP02_0134E", "profile"),
            "num_hungarian" : DataType("DP02_0135E", "profile"),
            "num_irish" : DataType("DP02_0136E", "profile"),
            "num_italian" : DataType("DP02_0137E", "profile"),
            "num_lithuanian" : DataType("DP02_0138E", "profile"),
            "num_norwegian" : DataType("DP02_0139E", "profile"),
            "num_polish" : DataType("DP02_0140E", "profile"),
            "num_portuguese" : DataType("DP02_0141E", "profile"),
            "num_russian" : DataType("DP02_0142E", "profile"),
            "num_scotch-irish" : DataType("DP02_0143E", "profile"),
            "num_scottish" : DataType("DP02_0144E", "profile"),
            "num_slovak" : DataType("DP02_0145E", "profile"),
            "num_subsaharan_african" : DataType("DP02_0146E", "profile"),
            "num_swedish" : DataType("DP02_0147E", "profile"),
            "num_swiss" : DataType("DP02_0148E", "profile"),
            "num_ukrainian" : DataType("DP02_0149E", "profile"),
            "num_welsh" : DataType("DP02_0150E", "profile"),
            "num_west_indian_(excluding_hispanic_origin_groups)" : DataType("DP02_0151E", "profile"),

        }
        # this is useful when writing out citations, having what each of the individual data
        # tables are called.
        self.table_names = {
            "DP02" : "Selected Social Characteristics in the United States",
            "DP05" : "Demographic and Housing Estimates",
            "B25001" : "Housing Units",
            "S1101" : "Households and Families",
            "S0101" : "Age and Sex",
            "S1901" : "Income in the Past 12 Months (in 2022 Inflation-Adjusted Dollars)",
            "S1701" : "Poverty Status in the Past 12 Months",
            "S1902" : "Mean Income in the Past 12 Months (in 2022 Inflation-Adjusted Dollars)"
        }

    # return a dictionary of all the acs data that seems feasibly relevant, namely
    # the ones initialized init_acs_params
    # keys are names like "num_households" and the values are numbers like
    # the actual number of households
    def get_all_acs_data(self):
        self.init_acs_params()
        our_data = self.get_all_acs_params_fewer_queries(self.params)

        # KEEPING UNUSED CODE AS IT MAY BE MORE RELIABLE OR SOMETHING?
        # (as in if something breaks, I want to have this here to fall back on)

        # apply get_acs_data to all values in the dictionary
        # and return this modified dictionary
        # our_data = {k : self.get_acs_data(self.params[k]) for k in self.params.keys()}
        # # density is number of people/area

        # gotta add this manually, since it's not strictly part of acs rather,
        # part of Gazetteer data
        our_data["land_area"] = self.get_land_area_of_city()
        return our_data

    def get_all_acs_params_fewer_queries(self, params_dict):
        filled_in_dict = {}
        # UPDATE IF: there's another location used in our queries
        for location in ["subject", "profile", ""]:
            # key is of type string, params_dict[key] will be of type "DataType"
            params_tuple = [(key, params_dict[key]) for key in params_dict.keys()
                                if params_dict[key].LOCATION == location] # if we're currently querying that location
            # sort by the specific data table location. Sorting is based on the lexicographical
            # ordering of where in the data table it is (e.g. DP_02_0101E)
            params_tuple.sort(key = lambda indv_tuple: indv_tuple[1].NAME)
            # get the right data extension by getting the first tuple, and the DataType
            # object from it
            data_extension = self.get_data_extension(params_tuple[0][1])
            left_to_query = params_tuple
            while len(left_to_query) != 0:
                # limit of querying 50 pieces od data at a time
                currently_querying = left_to_query[:50]

                # want to join the various places we're querying
                query_values = ','.join([data_object.NAME for (_, data_object) in currently_querying])
                output = self.get_data_from_table(data_extension,
                                                self.MOST_RECENT_ACS5_DATE,
                                                query_values).text

                relevant_output = eval(output)[1]
                # match the results of the query to their corresponding named
                # things
                for (index, (key, _)) in enumerate(currently_querying):
                    filled_in_dict[key] = relevant_output[index]
                # we've queried the first 50 elements so move forward 50 elements
                left_to_query = left_to_query[50:]

        # # [1] gets the list of the actual response to my query
        # # [0] gets the data that I want
        # return (eval(output))[1][0]
        return filled_in_dict

    # to be implemented if there's a desire for it :-)
    def get_all_decennial_census_data(self):
        pass

    # what the part after the base piece of the query is before the query
    # itself
    def get_data_extension(self, data_type_object):
        if self.use_acs1:
            data_extension = "acs/acs1"
        else:
            data_extension = "acs/acs5"
        # handle things from the b-range
        if data_type_object.LOCATION != "":
            data_extension += "/" + data_type_object.LOCATION
        return data_extension

    def get_acs_data(self, data_type_object):
        # using eval to turn the output into a list (I trust the US Census
        # not to give me malicious responses to queries. If you don't, look here:
        # https://stackoverflow.com/questions/1894269/how-to-convert-string-representation-of-list-to-a-list)

        data_extension = self.get_data_extension(data_type_object)
        if self.use_acs1:
            output = self.get_data_from_table(data_extension,
                                            self.MOST_RECENT_ACS1_DATE,
                                            data_type_object.NAME).text
        else:
            output = self.get_data_from_table(data_extension,
                                            self.MOST_RECENT_ACS5_DATE,
                                            data_type_object.NAME).text
        # [1] gets the list of the actual response to my query
        # [0] gets the data that I want
        return (eval(output))[1][0]

    # must download the most recent places data from here
    # to work https://www.census.gov/geographies/reference-files/time-series/geo/gazetteer-files.html
    # and it must be in the same folder as this python program
    def get_land_area_of_city(self):
        # place info is the state id + the place id
        full_place_info = self.location_info["state"] + self.location_info["place"]
        # change this title when Gazetteer files change
        with open("2023_Gaz_place_national.txt", "r") as places:
            # each individual place is demarcated by a new line
            text = places.read()
            formatted_nicer = text.split("\n")
            # print(formatted_nicer[5])
            # split on tabs (also strip ridiculous amount of whitespace at end)
            formatted_even_nicer = [place_entry.strip().split("\t") for place_entry in formatted_nicer]
            # print(formatted_even_nicer[5])
            # loop through all the places
            for x in formatted_even_nicer:
                if x[1] == full_place_info:
                    # x[8] is sorta just where land area is
                    return x[8]
            # [9] has square mile land area
    # returns the info for New London city, CT as of 2022 ACS5 or whatever, so we don't
    # have to requery every time we want to test
    def return_testing_data(self):
        return {'num_25_to_29': '2101', 'num_30_to_34': '1481', 'num_35_to_39': '2088', 'num_40_to_44': '1728', 'num_45_to_49': '1381', 'num_50_to_54': '1328', 'num_55_to_59': '1845', 'num_60_to_64': '1679', 'num_under_18': '4553', 'num_18_to_24': '5349', 'num_65_and_over': '4063', 'median_age': '35.5', 'num_families': '5682', 'num_with_determined_poverty_status': '23743', 'num_minors_status_determined': '4463', 'num_seniors_status_determined': '3894', 'num_male_status_determined': '11457', 'num_female_status_determined': '12286', 'num_below_poverty_level': '5108', 'num_minors_below_poverty_level': '1624', 'num_seniors_below_poverty_level': '431', 'num_male_below_poverty_level': '2453', 'num_female_below_poverty_level': '2655', 'median_income_household_overall': '56237', 'median_income_household_family': '65357', 'median_income_household_non_family': '46119', 'per_capita_income': '30943', 'num_households': '11125', 'num_households_married': '3046', 'num_households_cohabitating': '1193', 'num_households_male_sans_partner': '3090', 'num_households_male_sans_partner_w_children': '161', 'num_households_female_sans_partner': '3796', 'num_households_female_sans_partner_w_children': '705', 'num_households_with_minors': '2632', 'num_households_with_seniors': '3252', 'average_household_size': '2.12', 'average_family_size': '2.84', 'num_american': '474', 'num_arab': '112', 'num_czech': '70', 'num_danish': '62', 'num_dutch': '163', 'num_english': '2007', 'num_french_(except_basque)': '433', 'num_french_canadian': '695', 'num_german': '1511', 'num_greek': '86', 'num_hungarian': '86', 'num_irish': '3025', 'num_italian': '2713', 'num_lithuanian': '37', 'num_norwegian': '148', 'num_polish': '948', 'num_portuguese': '307', 'num_russian': '321', 'num_scotch-irish': '219', 'num_scottish': '421', 'num_slovak': '143', 'num_subsaharan_african': '202', 'num_swedish': '369', 'num_swiss': '54', 'num_ukrainian': '50', 'num_welsh': '35', 'num_west_indian_(excluding_hispanic_origin_groups)': '1052', 'total_population': '27596', 'male_population': '13359', 'female_population': '14237', 'males_per_hundred_females': '93.8', 'under_18_population': '4553', 'num_one_race': '24602', 'num_two_or_more_race': '2994', 'num_solely_white': '15512', 'num_solely_black_or_african_american': '4694', 'num_solely_american_indian_or_alaska_native': '91', 'num_solely_asian': '648', 'num_solely_native_hawaiian_or_other_pacific_islander': '0', 'num_solely_some_other_race': '3657', 'num_white': '17926', 'num_black_or_african_american': '6189', 'num_american_indian_or_alaska_native': '441', 'num_asian': '850', 'num_native_hawaiian_or_other_pacific_islander': '46', 'num_some_other_race': '5288', 'num_hispanic_or_latino': '8104', 'num_housing_units': '12239', 'land_area': '5.607'}


# thing to demarcate when we want to add in all the citations
# that have "built up"
class PlaceToAddCitation:
    def __init__(self):
        pass

# TODO: Make all of these param classes a sub-class of a larger
# param class that has the helper "get_data"
# indicates a param to be filled in with the actual
# data, so just something we wanna look up in a dictionary,
# like num_people
class ParamName():
    def __init__(self, string_name):
        self.name = string_name

class PercentageOfParam():
    # used to store params that we want to have that
    # subset param is x% of total_param, for example subset could
    # be male population and total param would be overall population
    # and we'd want to know what percent is male
    def __init__(self, subset_param_name, total_param_name, num_decimal_digits = 1):
        self.subset_param_name = subset_param_name
        self.total_param_name = total_param_name
        self.num_decimal_digits = num_decimal_digits

class RatioParam():
    # used to store params that we want to have that
    # there are x of param_x for every one param_y.
    # this is gonna be used for density
    def __init__(self, param_x, param_y, num_decimal_digits = 1):
        self.param_x = param_x
        self.param_y = param_y
        self.num_decimal_digits = num_decimal_digits

class SortedPercentageParams:
    # when we want to sort a bunch of params (for instance, it makes sense
    # for racial makeup to be ordered based on how many people are of a certain
    # race, so if Asian folks are the most common, they should be listed first)
    def __init__(self, list_of_params, total_param_name, threshold = 0):
        # each element is formatted as (text after percentage, Param)
        self.list_of_params = list_of_params
        # note that for comparission of percentages to make sense the denominator
        # really oughta be the same I think??
        self.total_param_name = total_param_name
        # what's the minimum threshold to be included in the text, 0 means
        # that everything is included
        self.threshold = threshold


# the ancestry params are weird, so just deal with it in a seperate thing
class SortedPercentageParamsAncestry:
    def __init__(self, list_of_params, total_param_name, threshold = 0):
        # each element is formatted as (wiki-linked-ancestry, Param)
        self.list_of_params = list_of_params
        # note that for comparission of percentages to make sense the denominator
        # really oughta be the same I think??
        self.total_param_name = total_param_name
        # what's the minimum threshold to be included in the text, 0 means
        # that everything is included
        self.threshold = threshold

class SumPercentageParams:
    # when we want to find a percentage with sum values in more than one param,
    # such as finding the percentage of people between 25 and 44 being the sum of
    # 25–29 + 30–34 + ... + 40–44 over the total number of folks
    def __init__(self, list_of_params, total_param):
        self.list_of_params = list_of_params
        self.total_param = total_param

# returns a string with all the info and
# citations necessary to just copy and
# paste it into Wikipedia. Note that the Shibboleth
# for invalid data is -888888888, so if you see
# that one of the query is wrong, and you should
# let me (GrapeRocks) know on my talkpage
class CensusWriter():

    def __init__(self, API_Key, test_mode = False):
        self.getter = CensusGetter(API_Key)
        # if test_mode is true, then we just use the data from New London that I've copied
        # and pasted so we don't have to query a bunch just to test formatting
        self.test_mode = test_mode
        # list of all references used so far, only really used in one
        # function,,, so it probably should just be a local variable, but
        # whatever
        self.all_references_used = set()
        # whether to include the place the reference refers to,
        # so New London table S0101 would be "S0101-09-52280",
        # in case you want to use this script to get more than one cities'
        # information, CURRENTLY NOT IMPLEMENTED
        self.verbose_ref_names = False

        #### SETTINGS ####
        # how many decimal places go after percentages
        self.NUM_DECIMAL_PLACES_PERCENTAGES = 1
        # how many decimal places go after ratios such as
        # population density
        self.NUM_DECIMAL_PLACES_RATIO = 1
        # must have at least 0.5% of the population a certain ancestry to include it
        self.ANCESTRY_THRESH = 0.5

        # what percent of people must solely identify as a race
        # to be listed (i.e. 0.1% must identify as a race to be reported)
        self.SOLE_RACE_THRESHOLD_PER = 0.1
        # same, but double count folks who identify as more than one race
        self.ALL_RACE_THRESHOLD_PER = 0.2

        # this setting currently doesn't work
        # what percentage point difference a subgroup must show
        # from the base line to be included (so if the general public
        # has a property 20% of the time and the threshold rate is
        # 0.05 then if minors have the property less than 15% of the time
        # or more than 25% of the time, then it'll include the sub-group).
        # this is a rather sloppy way to get at statistical signific
        # and I should prolly use the one that they include, but this probably
        # works for now
        self.DIFF_FOR_SUBGROUP_REPORTED = 0.05

    # see set_place comment in CensusGetter for more info about place_info
    def format_option_one_acs(self, place_info):
        # QUESTION: Generally, what data should I include that I don't. What data
        # should I cut that I do?
        self.getter.set_place(place_info)

        # {{As of|date|pre=the}} displays as "as of the [date]"
        # https://en.wikipedia.org/w/index.php?title=Arlington,_Washington&oldid=1228808199#2010_census
        # gives how I formatted the density cetion
        elements = ["{{As of|", str(self.getter.MOST_RECENT_ACS5_DATE), "|pre=the}} [[American Community Survey]]" +\
                    " estimates, there were ", ParamName("total_population"),
                    " people and ", ParamName("num_households"), " households.", PlaceToAddCitation(),
                    " The [[population density]] was {{convert|",
                    RatioParam("total_population", "land_area"), "|PD/sqmi|PD/km2|1}}.",
                    " There were ", ParamName("num_housing_units"), " housing units at an average density of ",
                    "{{convert|", RatioParam("total_population", "num_housing_units"), "|/sqmi|/km2|1}}.",
                    PlaceToAddCitation()]
        # QUESTION: some of the races are pretty verbose, should they be shorter, if so to what?
        # QUESTION: should solely some other race be included in the sort, or be at the end?
        elements.extend([
                " The racial makeup of the city was ",
                SortedPercentageParams(
                    [
                        # use non-breaking spaces cause it looks nicer or something?
                        ("%&nbsp;White", ParamName("num_solely_white")),
                        ("%&nbsp;Black or African American", ParamName("num_solely_black_or_african_american")),
                        ("%&nbsp;Native American or Alaskan Native", ParamName("num_solely_american_indian_or_alaska_native")),
                        ("%&nbsp;Asian", ParamName("num_solely_asian")),
                        ("%&nbsp;Native Hawaiian or Other Pacific Islander", ParamName("num_solely_native_hawaiian_or_other_pacific_islander")),
                        ("%&nbsp;some other race", ParamName("num_solely_some_other_race"))],
                    "total_population" # all the percentages are over total population
                ),
                ", with ", PercentageOfParam("num_two_or_more_race", "total_population"),
                "&nbsp;from two or more races.", PlaceToAddCitation()
        ])

        # Hispanic/Latino bit from
        # https://en.wikipedia.org/w/index.php?title=Stephens_City,_Virginia&oldid=1222587193#Demographics
        elements.extend([" [[Hispanic and Latino Americans|Hispanics or Latinos]] of any race were ",
                        PercentageOfParam("num_hispanic_or_latino", "total_population"),
                        "&nbsp;of the population.", PlaceToAddCitation()])

        # household demographics courtesy largely of New London's page, and some of the nittier
        # grittier formatting from Stephen City (like the "of the" language). I'm not sorting for
        # now
        # QUESTION: which if any elements of this paragraph should be sorted?
        elements.extend(
            [
                "\n\n", "Of the ", ParamName("num_households"), " households, ",
                PercentageOfParam("num_households_with_minors", "num_households"),
                "&nbsp;had children under the age of 18 living with them, ",
                PercentageOfParam("num_households_with_seniors", "num_households"),
                "&nbsp;had seniors 65 years or older living with them, ",
                PercentageOfParam("num_households_married", "num_households"),
                "&nbsp;were married couples living together, ",
                PercentageOfParam("num_households_cohabitating", "num_households"),
                "&nbsp;were couples cohabitating, ",
                PercentageOfParam("num_households_male_sans_partner", "num_households"),
                "&nbsp;had a male householder with no partner present, and ",
                PercentageOfParam("num_households_female_sans_partner", "num_households"),
                "&nbsp;had a female householder with no partner present.", PlaceToAddCitation(),
                " The median household size was ", ParamName("average_household_size"), " and ",
                "the median family size was ", ParamName("average_family_size"), ".", PlaceToAddCitation()
            ]
        )
        # ages, format courtesy of
        # https://en.wikipedia.org/w/index.php?title=Stephens_City,_Virginia&oldid=1222587193#Demographics
        elements.extend(
            [
                "\n\n", "The age distribution was ", PercentageOfParam("num_under_18", "total_population"),
                "&nbsp;under 18, ", PercentageOfParam("num_18_to_24", "total_population"),
                "&nbsp;from 18 to 24, ",
                SumPercentageParams(
                    [
                        "num_25_to_29", "num_30_to_34", "num_35_to_39", "num_40_to_44"
                    ], "total_population"
                ), "&nbsp;from 25 to 44, ",
                SumPercentageParams(
                    [
                        "num_45_to_49", "num_50_to_54", "num_55_to_59", "num_60_to_64"
                    ], "total_population"
                ), "&nbsp;from 45 to 64, and ",
                PercentageOfParam("num_65_and_over", "total_population"),
                "&nbsp;who were 65 or older. The median age was ", ParamName("median_age"),
                " years.", PlaceToAddCitation()
            ]
        )
        # household stuff, also from Stephens City
        elements.extend(
            [
                "\n\n", "The median income for a household was $", ParamName("median_income_household_overall"),
                ", with family households having a median income of $", ParamName("median_income_household_family"),
                " and non-family households $", ParamName("median_income_household_non_family"),
                ". The [[per capita income]] was $", ParamName("per_capita_income"), ".",
                PlaceToAddCitation()
            ]
        )

        # poverty status, from my own brain, I think?
        elements.extend(
            [
                " Out of the ", ParamName("num_with_determined_poverty_status"), " population with a determined ",
                "poverty status, ", PercentageOfParam("num_below_poverty_level", "num_with_determined_poverty_status"), "&nbsp;were below the [[poverty line]].",
                " Further, ", PercentageOfParam("num_minors_below_poverty_level", "num_minors_status_determined"),
                "&nbsp;of minors and ",
                PercentageOfParam("num_seniors_below_poverty_level", "num_seniors_status_determined"),
                "&nbsp;of seniors were below the poverty line.", PlaceToAddCitation()
            ]
        )
        # household stuff, also from Stephens City. First sentence mostly copied
        elements.extend(
            [
                "\n\n", "In the survey, residents self-identified with various ethnic ancestries. ",
                SortedPercentageParamsAncestry(
                    [
                        ("[[American ancestry|American]]", ParamName("num_american")),
                        ("[[Arab American|Arab]]", ParamName("num_arab")),
                        ("[[Czech American|Czech]]", ParamName("num_czech")),
                        ("[[Danish American|Danish]]", ParamName("num_danish")),
                        ("[[Dutch American|Dutch]]", ParamName("num_dutch")),
                        ("[[English American|English]]", ParamName("num_english")),
                        # QUESTION: what does the except Basque here even mean???????
                        ("[[French American|French]]", ParamName("num_french_(except_basque)")),
                        ("[[French Canadian American|French Canadian]]", ParamName("num_french_canadian")),
                        ("[[German American|German]]", ParamName("num_german")),
                        ("[[Greek American|Greek]]", ParamName("num_greek")),
                        ("[[Hungarian American|Hungarian]]", ParamName("num_hungarian")),
                        ("[[Irish American|Irish]]", ParamName("num_irish")),
                        ("[[Italian American|Italian]]", ParamName("num_italian")),
                        ("[[Lithuanian American|Lithuanian]]", ParamName("num_lithuanian")),
                        ("[[Norwegian American|Norwegian]]", ParamName("num_norwegian")),
                        ("[[Polish American|Polish]]", ParamName("num_polish")),
                        ("[[Portuguese American|Portuguese]]", ParamName("num_portuguese")),
                        ("[[Russian American|Russian]]", ParamName("num_russian")),
                        ("[[Scotch-Irish American|Scotch-Irish]]", ParamName("num_scotch-irish")),
                        ("[[Scottish American|Scottish]]", ParamName("num_scottish")),
                        ("[[Slovak American|Slovak]]", ParamName("num_slovak")),
                        ("[[Sub-Saharan Africa|Sub-Saharan African]]", ParamName("num_subsaharan_african")),
                        ("[[Swedish American|Swedish]]", ParamName("num_swedish")),
                        ("[[Swiss American|Swiss]]", ParamName("num_swiss")),
                        ("[[Ukrainian American|Ukrainian]]", ParamName("num_ukrainian")),
                        ("[[Welsh American|Welsh]]", ParamName("num_welsh")),
                        # west indian is the same thing as Carribean, and that feels like a more
                        # accurate term to use
                        ("[[Caribbean American|Caribbean (excluding hispanics)]]", ParamName("num_west_indian_(excluding_hispanic_origin_groups)")),
                    ], "total_population"
                ),
                ".", PlaceToAddCitation()
            ]
        )

        return self.read_elements_acs(elements)

    def read_elements_acs(self, elements):
        full_string = ""
        self.getter.init_acs_params()
        # if we're in testing mode use pre-gotten data
        if self.test_mode:
            dict_data = self.getter.return_testing_data()
        else:
            # otherwise, fetch it from scratch
            dict_data = self.getter.get_all_acs_data()
        # print(dict_data)
        new_references = set()
        for element in elements:
            if type(element) == PlaceToAddCitation:
                # add all built up citations to the string
                for ref in new_references:
                    if ref in self.all_references_used:
                        # how we represent the reference like
                        # <ref name="potato"> information </ref> is by getting
                        # everything before the first > and adding /> to that
                        actual_ref = ref.split(">")[0] + "/>"
                        full_string += actual_ref
                    # otherwise, we've never seen this reference before, so just
                    # use it as normal
                    else:
                        full_string += ref
                # put everything in new_refs into refs_used
                self.all_references_used.update(new_references)
                # and clear the set of new references cause we've just cited them
                # all
                new_references = set()

            elif type(element) == ParamName:
                # add the corresponding data

                # QUESTION: should this not use format num cause it's too cluttered?
                full_string += "{{formatnum:" + dict_data[element.name] + "}}"
                # whenever you see this weird {:,} notation, that's just to add commas to stuff
                # full_string += "{:,}".format(int(dict_data[element.name]))
                new_references.add(self.getter.get_named_reference_for_param_acs(element.name))

            elif type(element) == PercentageOfParam:
                # multiply the fraction by 100 to get a percentage and then
                # round it to.
                full_string += str(round(float(dict_data[element.subset_param_name])\
                                        / float(dict_data[element.total_param_name]) * 100, self.NUM_DECIMAL_PLACES_PERCENTAGES))
                # add the percent sign, lol
                full_string += "%"
                new_references.add(self.getter.get_named_reference_for_param_acs(element.subset_param_name))
                # almost always, we'll have talked about total param before we mention a percentage,
                # so do we have to re-cite this?? Like, we'll talk about population in the first
                # sentence, and then talk about what percentage of the population has a feature,
                # should we cite a source for the total number of people? This might be a moot point
                # since most/all tables where its relevant has the number of people, so we don't need
                # to re-cite the original source anyway
                # QUESTION: should the denominator be cited in percentages?
                # new_references.add(self.getter.get_named_reference_for_param_acs(element.total_param_name))

            elif type(element) == RatioParam:
                # QUESTION: Should I use round?
                full_string += str(round(float(dict_data[element.param_x])\
                                        / float(dict_data[element.param_y]), self.NUM_DECIMAL_PLACES_RATIO))
                # we've used both of these data sources. Citing both is important cause param_y is
                # stuff like land_area which we don't actually cite in the body
                new_references.add(self.getter.get_named_reference_for_param_acs(element.param_x))
                new_references.add(self.getter.get_named_reference_for_param_acs(element.param_y))

            elif type(element) == SortedPercentageParams:
                # add all the references (not including the total_population one (for now))
                for (_, param) in element.list_of_params:
                    new_references.add(self.getter.get_named_reference_for_param_acs(param.name))

                sorted_list_of_per_tuples = self.get_sorted_list_of_params_percentages(element, dict_data)
                # UPDATE if: we ever use sorted percentage params for something other than
                # sole race (probably would be stuff about marriage, but who knows.). Anyways,
                # really should use the .threshold thing that's part of this class, but hey.
                # (also all of these should be broken out into the individual classes before
                # release)
                sorted_list_of_per_tuples = list(filter(lambda param: param[1] >= self.SOLE_RACE_THRESHOLD_PER,
                                                   sorted_list_of_per_tuples))
                # now that we've (probably) sorted in order, we gotta add them to our list, including Oxford comma
                # and the like
                for (index, item) in enumerate(sorted_list_of_per_tuples):
                    # if we're at the end of the list we want an and
                    if index == len(sorted_list_of_per_tuples) - 1:
                        # if there's exactly one element, we don't want an and
                        if len(sorted_list_of_per_tuples) != 1:
                            full_string += "and "

                    # get the text of our param
                    full_string += str(item[1])
                    # the text we want after the param
                    full_string += item[0]

                    # if we're not at the end of the list, add a comma
                    if index != len(sorted_list_of_per_tuples) - 1:
                        # only want commas if there's more than 2 elements
                        if len(sorted_list_of_per_tuples) > 2:
                            full_string += ", "

            elif type(element) == SortedPercentageParamsAncestry:
                # add all the references (not including the total_population one (for now))
                for (_, param) in element.list_of_params:
                    new_references.add(self.getter.get_named_reference_for_param_acs(param.name))
                sorted_list_of_per_tuples = self.get_sorted_list_of_params_percentages(element, dict_data)
                # get rid of any items below the ancestry threshold cut off
                sorted_list_of_per_tuples = list(filter(lambda param: param[1] >= self.ANCESTRY_THRESH,
                                                   sorted_list_of_per_tuples))
                for (index, item) in enumerate(sorted_list_of_per_tuples):
                    # if we're at the end of the list we want an and
                    if index == len(sorted_list_of_per_tuples) - 1:
                        # don't want an and if there's exactly one item
                        if len(sorted_list_of_per_tuples) != 1:
                            full_string += "and "
                    if index == 0:
                        full_string += "People of "
                    # the wiki-linked text of say [[American]]
                    full_string += item[0]
                    # if it's the first we want fancier per Stephens City format
                    if index == 0:
                        full_string += " descent make up "
                    else:
                        full_string += " at "
                    # add the percentage
                    full_string += str(item[1]) + "%"
                    # if we're at the start, introduce what we're taking a percentage of,
                    # and introduce the next item
                    if index == 0:
                        full_string += "&nbsp;of the population of the town, followed by "
                    # if we're not at the end, we want a comma
                    elif index != len(sorted_list_of_per_tuples) - 1:
                        # if we have more than two items, we need comma separation
                        if len(sorted_list_of_per_tuples) > 2:
                            full_string += ", "


            elif type(element) == SumPercentageParams:
                # counter thingy
                total_subset_size = 0
                # go through and up the corresponding value
                for sub_element in element.list_of_params:
                    total_subset_size += int(dict_data[sub_element])
                # percentage is the total of the subgroup/total of whole group
                full_string += str(round(total_subset_size /
                                        float(dict_data[element.total_param]) * 100, self.NUM_DECIMAL_PLACES_PERCENTAGES))
                # add the percent sign, lol
                full_string += "%"

            # if it's a string, then we just wanna straight up and add it
            elif type(element) == str:
                full_string += element

        return full_string

    # both Sorted and SortedAncestry have mostly the same format, and they
    # notably both need to be sorted collections of params, so break the function
    # out and do it in one place
    def get_sorted_list_of_params_percentages(self, element, dict_data):
        unrounded = sorted(
            [(text,
                    float(dict_data[item.name]) # item name is the larger quantity
                    / float(dict_data[element.total_param_name]) * 100)
                for (text, item) in element.list_of_params
            ],
            key = lambda text_per_tuple: text_per_tuple[1], # lambda means we sort by what the percentage is
            reverse=True # means that we have highest percentage first
        )
        # round it after sorting to be mroe accurate
        return [
                    (text, round(per, self.NUM_DECIMAL_PLACES_PERCENTAGES))
                    for (text, per) in unrounded
                ]

    # obviously not implemented
    def new_london_format_mixed_data(self, place_info):
        # uses census data for exact figures like population
        # and acs for other figures.
        pass

# if test_mode is True then it will ignore the input to the function format_option_one_acs.
# having test_mode = False is good for testing out various formatting changes, to get more
# instantaneous results (though the ~10 second wait isn't terrible)
# h = CensusWriter("YOUR API KEY", test_mode=False)
# print(h.format_option_one_acs("IL|17|38570|02395477|Joliet city|INCORPORATED PLACE|C1|A|Kendall County~~~Will County"))

def thing_to_run():
    # TODO: I don't think the person strictly neeeeds an API key, cause I think they get
    # some number of queries without one, which is less than what this does, but currently
    # the code requires one, so, uh, think about updating it so it doesn't
    api_key = input("Please enter your API Key. If you do not have an API key you can go to " +
                    "https://api.census.gov/data/key_signup.html to get one: ")
    place_info = input("Please copy and paste the place info from " +
                       "https://www.census.gov/library/reference/code-lists/ansi.html place " +
                       "table row of your relevant city. Make sure it's the place table row" +
                       "And not the Place by County row. Please paste the whole row: ")

    print("WE\'RE NOW COOKING UP YOUR DATA, BE A LIL' PATIENT, WOULDJA? It usually takes " +
          "like TEN SECONDS??? USED TO TAKE A MINUTE :-DDD")
    h = CensusWriter(api_key)
    # now we're actually cooking up their data :-P
    the_string = h.format_option_one_acs(place_info)
    print("Great, it's now been prepared. Just as a reminder, you are vaguely responsible" +
          "for verifying the factual accuracy of the data and that the links and citations" +
          "are legit. They should be, but I'm certainly not responsible for anything" +
          "that you enter in that's wrong. That's on you")
    print()
    print("HERE IT IS:")
    print()
    print(the_string)
if __name__ == "__main__":
    thing_to_run()

