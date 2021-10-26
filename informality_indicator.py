import json
import math


file = open('Data/lomas_MongoDB.json')
settlement_data = json.load(file)


def identify_na(stat):
    if type(stat) == str or type(stat) == 'unicode':
        if stat == "" or stat == "n/a":
            return 50
        else:
            if type(stat) == int:
                return int(stat)
            else:
                return float(stat)
    elif stat == None:
        return 50
    else:
        return stat

def n_causes(cause):
    new_cause = cause.lower()
    if new_cause == "squatting":
        return 10
    elif new_cause == 'refugee camp':
        return 50
    elif new_cause == 'illegal subdivision':
        return 80
    elif new_cause == 'other':
        return 10
    else:
        return 50

def n_causes(cause):
    new_cause = cause.lower()
    if new_cause == "squatting":
        return 10
    elif new_cause == 'refugee camp':
        return 50
    elif new_cause == 'illegal subdivision':
        return 80
    elif new_cause == 'other':
        return 10
    else:
        return 50

def n_population(pop):
    if pop == "":
        return 0
    else:
        num = int(pop)
        if num <= 10000:
            return 80
        elif num > 10000 and num <= 50000:
            return 50
        elif num > 50000 and num <= 100000:
            return 30
        elif num > 100000 and num <= 1000000:
            return 10
        else:
            return 0

def n_topography(top):
    new_top = top.lower()
    if new_top == "desert":
        return 20
    elif new_top == "water":
        return 40
    elif new_top == "by the coast":
        return 80
    elif new_top == "valley":
        return 100
    elif new_top == "mountain":
        return 50
    elif new_top == "forest":
        return 60
    elif new_top == "other":
        return 10
    elif new_top == 'land':
        return 40
    else:
        return 50

def n_materials(mat):
    new_mat = mat.lower()
    if new_mat == "mud":
        return 65
    elif new_mat == "Brick":
        return 80
    elif new_mat == "concrete":
        return 100
    elif new_mat == "wood":
        return 70
    elif new_mat == "corrugated" or new_mat == "corrugated sheet":
        return 40
    elif new_mat == "tensile" or new_mat == "tarpaulin / tensile structures":
        return 20
    elif new_mat == "cardboard":
        return 10
    elif new_mat == "other":
        return 10
    else:
        return 50

def climate_materials(climate):
    if climate == 'A':
        return 80
    elif climate == 'C':
        return 90
    elif climate == 'B':
        return 80
    elif climate == 'D':
        return 90
    elif climate == 'E':
        return 50

def n_type_of_energy(energy):
    new_energy = energy.lower()
    if new_energy == "electricity":
        return 100
    elif new_energy == "lpg" or new_energy == "lpg, natural gas" or new_energy == "gas":
        return 75
    elif new_energy == "kerosene" or new_energy == "kerosene, other liquid fuel":
        return 45
    elif new_energy == "coal" or new_energy == "coal, lignite":
        return 40
    elif new_energy == "firewood, straw, dung or charcoal" or new_energy == "firewood":
        return 10
    elif new_energy == "other":
        return 10
    else:
        return 50

def n_type_of_energy_cooking(energy):
    new_energy = energy.lower()
    if new_energy == "electricity":
        return 100
    elif new_energy == "lpg":
        return 100
    elif new_energy == "kerosene":
        return 50
    elif new_energy == "coal":
        return 15
    elif new_energy == "firewood":
        return 10
    else:
        return 50

def n_type_of_mobility(mob):
    new_mob = mob.lower()
    if new_mob == "walk":
        return 10
    elif new_mob == "bike":
        return 50
    elif new_mob == "motorcycle":
        return 10
    elif new_mob == "animal":
        return 5
    elif new_mob == "tuctuc" or new_mob == "informal transportation, tuctuc":
        return 15
    elif new_mob == "microbus":
        return 20
    elif new_mob == "car":
        return 30
    elif new_mob == "bus" or new_mob == "public transportation, bus":
        return 40
    elif new_mob == "subway" or new_mob == "public transportation, subway":
        return 80
    elif new_mob == "by public transport":
        return 60
    elif new_mob == "other":
        return 10
    else:
        return 50


def round(num):
    integer = math.floor(num)
    decimal = num - integer
    if decimal <= 0.5:
        return integer + 0.25
    else:
        return integer + 0.75



def informality(data, access_energy_TeraScope):
    
    #Site-Origin

    causes = [n_causes(e) for e in data['site']['origin']['causes'] if e != ""][0]
    

    
    try:
        population = n_population(data['site']['origin']['population'])
    except:
        population = 50

    #Site-Geography
    topography = [n_topography(e) for e in data['site']['geography']['topography'] if e != ""][0]


    try:
        weather = identify_na(data['site']['vulnerability']['resilienceToNaturalConditions'])
    except KeyError:
        weather = 50
    
    type_of_climate = [climate_materials(e) for e in data['site']['geography']['type_of_climate'] if e != ""][0]
    


    #Site-Vulnerability
    #Inverse
    try:
        crime_rate = 100 - identify_na(data['site']['vulnerability']['crimeRate'])
    except KeyError:
        crime_rate = 50

    #Inverse
    try:
        perception_of_security = 100 - identify_na(data['site']['vulnerability']['perceptionOfInsecurity'])
    except KeyError:
        perception_of_security = 50

    try:
        participation = identify_na(data['site']['vulnerability']['communityEngagement'])
    except KeyError:
        participation = 50

    #Architecture-Physical Nature
    try:
        house_quality = identify_na(data['architecture']['physicalNature']['houseQuality'])
    except KeyError:
        house_quality = 50

    materials = [n_materials(e) for e in data['architecture']['physicalNature']['materials'] if e != ""][0]

    try:
        development_state = identify_na(data['architecture']['physicalNature']['developmentState'])
    except KeyError:
        development_state = 50

    #Architecture-Infraestructure
    try:
        access_to_energy = access_energy_TeraScope#identify_na(data['architecture']['infrastructure']['accessToEnergy'])
    except KeyError:
        access_to_energy = 50

    type_of_energy = [n_type_of_energy(e) for e in data['architecture']['infrastructure']['sourceOfEnergy'] if e != ""][0]


    try:
        access_to_water = identify_na(data['architecture']['infrastructure']['accessToWater'][0])
    except:
        access_to_water = 50

    try:
        water_public_private = identify_na(data['architecture']['infrastructure']['accessToWater'][1])/200 + 0.5
    except:
        water_public_private = 0.75

    try:
        access_to_sanitation = identify_na(data['architecture']['infrastructure']['accessToSanitation'][0])
    except:
        access_to_sanitation = 50

    try:
        sanitation_communal_private = identify_na(data['architecture']['infrastructure']['accessToSanitation'][1])/200 + 0.5
    except:
        sanitation_communal_private = 0.75

    try:
        telecommunications = identify_na(data['architecture']['infrastructure']['accessToPhoneFare'])
    except KeyError:
        telecommunications = 50

    try:
        internet = identify_na(data['architecture']['infrastructure']['accessToInternet'])
    except KeyError:
        internet = 50

    try:
        street_quality = identify_na(data['architecture']['infrastructure']['physicalStateOfStreets'])
    except KeyError:
        street_quality = 50
    
    type_of_mobility = [n_type_of_mobility(e) for e in data['architecture']['infrastructure']['mobilitySystems'] if e != ""][0]

    #Architecture-density
    try:
        elevation = identify_na(data['architecture']['density']['elevation'])
    except KeyError:
        elevation = 50

    try:
        household = identify_na(data['architecture']['density']['householdPerHouseSize'])
    except KeyError:
        household = 50

    ratio = data['architecture']['density']['ratio']

    #Populace-quality of life
    try:
        happiness = identify_na(data['populace']['qualityOfLife']['happiness'])
    except KeyError:
        happiness = 50

    try:
        access_to_food = identify_na(data['populace']['qualityOfLife']['food'])
    except KeyError:
        access_to_food = 50

    try:
        access_to_health = identify_na(data['populace']['qualityOfLife']['accessToHealthCare'])
    except KeyError:
        access_to_health = 50

    try:
        number_of_hospitals = identify_na(data['populace']['qualityOfLife']['numberOfHealthCareFacilities'])
        if number_of_hospitals == 0:
            number_of_hospitals = 1
    except KeyError:
        number_of_hospitals = 3

    #Populace-Economy
    #Inverse
    try:
        unemployment = 100 - identify_na(data['populace']['economy']['unemploymentRate'])
    except KeyError:
        unemployment = 50

    #Inverse
    try:
        formal_sector = 100 - identify_na(data['populace']['economy']['formalEmployment'])
    except KeyError:
        formal_sector = 50

    try:
        income = identify_na(data['populace']['economy']['populationIncome'])
    except KeyError:
        income = 50

    try:
        tenure = identify_na(data['populace']['economy']['tenure'])
    except KeyError:
        tenure = 50

    try:
        green_space = identify_na(data['populace']['qualityOfLife']['AccesstoNaturalsettings'])
    except:
        green_space = 50

    try:
        amenities = identify_na(data['populace']['qualityOfLife']['proximity'])
    except KeyError:
        amenities = 50

    #Populace-Demography
    try:
        gender = identify_na(data['populace']['demography']['gender'])

        if gender <= 0 or gender >= 100:
            gender = 0.01
    except KeyError:
        gender = 50

    try:
        zero_to_five = identify_na(data['populace']['demography']['ageGroups']['0-5years'])

        if zero_to_five == 0:
            zero_to_five = 0.01

        six_to_twelve = identify_na(data['populace']['demography']['ageGroups']['6-12years'])

        if six_to_twelve == 0:
            six_to_twelve = 0.01

        thirteen_to_eighteen = identify_na(data['populace']['demography']['ageGroups']['13-18years'])

        if thirteen_to_eighteen == 0:
            thirteen_to_eighteen = 0.01
        
        nineteen_to_thirty = identify_na(data['populace']['demography']['ageGroups']['19-30years'])

        if nineteen_to_thirty == 0:
            nineteen_to_thirty = 0.01

        thirtyone_to_fifty = identify_na(data['populace']['demography']['ageGroups']['31-50years'])

        if thirtyone_to_fifty == 0:
            thirtyone_to_fifty = 0.01

        over_fifty = identify_na(data['populace']['demography']['ageGroups']['50+years'])

        if over_fifty == 0:
            over_fifty = 0.01

        if sum([zero_to_five, six_to_twelve, thirteen_to_eighteen, nineteen_to_thirty, thirtyone_to_fifty, over_fifty]) == 0:
            zero_to_five = 100/6
            six_to_twelve = 100/6
            thirteen_to_eighteen = 100/6
            nineteen_to_thirty = 100/6
            thirtyone_to_fifty = 100/6
            over_fifty = 100/6
    except:
        zero_to_five = 100/6

        six_to_twelve = 100/6

        thirteen_to_eighteen = 100/6

        nineteen_to_thirty = 100/6

        thirtyone_to_fifty = 100/6

        over_fifty = 100/6

    

    try:
        access_to_education = identify_na(data['populace']['demography']['accessToEducation'])
    except:
        access_to_education = 50

    # maybe use a database
    popslum_per_country = 50

    try:
        area = data['geolocation']['area']
    except:
        area = 5

    num_population = data['site']['origin']['population']

    if num_population == None:
        num_population = 1000


    

    security = (perception_of_security + crime_rate)/2

    energy = development_state * 0.6 + (access_to_energy * 0.7 + type_of_energy * 0.3) * 0.4

    sanitation = access_to_sanitation * sanitation_communal_private

    water = access_to_water * water_public_private

    connectivity = 0.5 * telecommunications + 0.5 * internet

    mobility = street_quality * 0.6 + type_of_mobility * 0.4

    household_per_house = (-0.060024 + 1.458378*math.exp(-0.3190336*household/11))*100

    if household_per_house < 0:
        household_per_house = 0
    elif household_per_house > 100:
        household_per_house = 100

    health = 0.3 * (population/number_of_hospitals) + 0.7 * access_to_health

    jobs = income * 0.5 + formal_sector * 0.2 + unemployment * 0.3

    ownership = (1.23236 - 1.23242*math.exp(-1.6971*tenure/100))*100

    city_dependant = (green_space +  amenities)/2

    shanon_gender = abs((math.log(gender/100)*(gender/100) + math.log(1 - gender/100)*(1 - gender/100))/math.log(2))*100

    shanon_age = abs(math.log(zero_to_five/100)*(zero_to_five/100) + math.log(six_to_twelve/100)*(six_to_twelve/100) + math.log(thirteen_to_eighteen/100)*(thirteen_to_eighteen/100) + math.log(nineteen_to_thirty/100)*(nineteen_to_thirty/100) + math.log(thirtyone_to_fifty/100)*(thirtyone_to_fifty/100) + math.log(over_fifty/100)*(over_fifty/100))/math.log(6)*100
    shanon_age = 50
    #Inverse
    diversity = 100 - (shanon_age + shanon_gender)/2

    equity = 100 - shanon_age

    education = (-0.4422671 + 1.422244*math.exp(-0.01449828*access_to_education))*100

    if education < 0:
        education = 0

    
    i_topography = (topography + weather)/2

    infrastructure = (energy + sanitation + water + connectivity + mobility)/5

    economy = (jobs + ownership + city_dependant)/3

    climate = (house_quality + weather + infrastructure + type_of_climate)/4

    i_within_cities = (i_topography + climate + infrastructure + economy)/4

    physical_nature = (house_quality + materials + development_state)/3

    density = (elevation + household_per_house)/2

    demography = (diversity + equity + education)/3

    prevalence = (popslum_per_country + economy + physical_nature + infrastructure + participation + security)/6

    vulnerability = (weather + security + prevalence)/3

    geography = topography*0.4 + i_within_cities*0.2 + climate*0.4

    i_causes = (causes + geography)/2

    origin = (i_causes + population)/2

    dignity = (ownership + security + happiness + access_to_food + participation)/5

    emotional_state = (economy + education + health + city_dependant + house_quality)/5

    quality_life = (dignity + health + emotional_state)/3

    # Indicators

    # Site
    site = (origin + geography + vulnerability)/3

    # Architecture
    architecture = (physical_nature + infrastructure + density)/3

    # Populace
    populace = (economy + demography + quality_life)/3

    # Informality
    informality_indicator = (site + architecture + populace)/3

    return [informality_indicator, site, architecture, populace, infrastructure]



informality_index = informality(settlement_data,0)
print(informality_index)


