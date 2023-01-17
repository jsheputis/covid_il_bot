import requests
from datetime import datetime, date, timedelta

IGNORE_DATA_OLDER_THAN = '2022-10-01'

# formats date to ISO 8601
def format_date(date):
    return date.strftime("%Y-%m-%d")

# takes date from IDPH source and strips time value
def import_date(date, add_day=False, cdc=False):
    if cdc:
        imported_date = datetime.strptime(date,"%Y-%m-%dT%H:%M:%S.%f")
    else:
        imported_date = datetime.strptime(date,"%Y-%m-%dT%H:%M:%S")
    if add_day:
        imported_date = imported_date + timedelta(1)
    formatted_date = format_date(imported_date)
    return formatted_date

# Pulls all data from IDPH and combines them to a single dictionary using the date as the key
def get_idph_data(today):

    # Get today's date and format it how needed
    #today = date.today()
    today_formatted = format_date(today)
    
    # data source for tests and deaths, both seem to be updating on different schedules so pulling from both
    case_url = "https://idph.illinois.gov/DPHPublicInformation/api/COVID19/CasesDeaths/getCaseDeathChange"
    case_url_2 = "https://idph.illinois.gov/DPHPublicInformation/api/COVIDExport/GetIllinoisCases"
    case_url_3 = "https://idph.illinois.gov/DPHPublicInformation/api/COVIDExport/GetCountyTestResultsTimeSeries?countyName=Illinois"

    # data source for hospital, ICU, and ventilator utilization
    hospital_url = "https://idph.illinois.gov/DPHPublicInformation/api/COVID/GetHospitalizationResults"

    # CDC vaccination data source
    cdc_vaccine_url = "https://data.cdc.gov/resource/unsk-b7fc.json?location=IL"

    # grab all the data sources
    case_data = requests.get(case_url)
    case_data_2 = requests.get(case_url_2)
    case_data_3 = requests.get(case_url_3)
    # print(test_data.json())
    hospital_data = requests.get(hospital_url)
    #vaccine_data = requests.get(vaccine_url)
    cdc_vaccine_data = requests.get(cdc_vaccine_url)

    # create a dictionary to combine all data by date
    combined_data = dict()

    # get relevant info for cases and deaths
    for day in case_data.json():
        day_date = day['Report_Date']
        day_cases = day['CaseChange']
        day_deaths = day['DeathChange']

        normalized_date = import_date(day_date)

        if normalized_date < IGNORE_DATA_OLDER_THAN or normalized_date > today_formatted:
            continue

        # add day if it doesn't exist
        if normalized_date not in combined_data:
            combined_data[normalized_date] = dict()

        combined_data[normalized_date]['cases'] = day_cases
        combined_data[normalized_date]['deaths'] = day_deaths

    # Secondary source, currently not providing tests data but checking for it if it does show up
    for day in case_data_2.json():
        day_date = day['testDate']
        day_cases = day['cases_change']
        day_deaths = day['deaths_change']
        day_tested = day['tested_change']

        normalized_date = import_date(day_date)
        
        if normalized_date < IGNORE_DATA_OLDER_THAN or normalized_date > today_formatted:
            continue

        # add day if it doesn't exist
        if normalized_date not in combined_data:
            combined_data[normalized_date] = dict()

        normalized_date = import_date(day_date)

        if 'cases' not in combined_data[normalized_date]:
            combined_data[normalized_date]['cases'] = day_cases
        if 'deaths' not in combined_data[normalized_date]:
            combined_data[normalized_date]['deaths'] = day_deaths
        if day_tested and day_tested > 0 and 'tested' not in combined_data[normalized_date]:
            combined_data[normalized_date]['tested'] = day_deaths

    # Third source, currently not providing tests data but checking for it if it does show up, seems same as data #2 but useful backup
    for day in case_data_3.json():
        day_date = day['testDate']
        day_cases = day['cases_change']
        day_deaths = day['deaths_change']
        day_tested = day['tested_change']

        normalized_date = import_date(day_date)
        
        if normalized_date < IGNORE_DATA_OLDER_THAN or normalized_date > today_formatted:
            continue

        # add day if it doesn't exist
        if normalized_date not in combined_data:
            combined_data[normalized_date] = dict()

        normalized_date = import_date(day_date)

        if 'cases' not in combined_data[normalized_date]:
            combined_data[normalized_date]['cases'] = day_cases
        if 'deaths' not in combined_data[normalized_date]:
            combined_data[normalized_date]['deaths'] = day_deaths
        if day_tested and day_tested > 0 and 'tested' not in combined_data[normalized_date]:
            combined_data[normalized_date]['tested'] = day_deaths

    # get relevant info for tests if new source found
    # for day in case_data.json():
    for day in []:
        day_tested = 0

        normalized_date = import_date(day_date)

        if normalized_date < IGNORE_DATA_OLDER_THAN or normalized_date > today_formatted:
            continue

        # add day if it doesn't exist
        if normalized_date not in combined_data:
            combined_data[normalized_date] = dict()

        combined_data[normalized_date]['tested'] = day_tested

    # get relevant info for hospitalizations, etc.
    for day in hospital_data.json()['HospitalUtilizationResults']:
        day_date = day['ReportDate']
        day_covid_vent = day['VentilatorInUseCOVID']
        day_covid_icu = day['ICUInUseBedsCOVID']
        day_covid_beds = day['TotalInUseBedsCOVID']
        
        # data delayed by one day, adjusting to match official reports
        normalized_date = import_date(day_date, add_day=True)

        if normalized_date < IGNORE_DATA_OLDER_THAN or normalized_date > today_formatted:
            continue

        # add day if it doesn't exist
        if normalized_date not in combined_data:
            combined_data[normalized_date] = dict()

        combined_data[normalized_date]['covid_vent'] = day_covid_vent
        combined_data[normalized_date]['covid_icu'] = day_covid_icu
        combined_data[normalized_date]['covid_beds'] = day_covid_beds

    # Ingest CDC data
    for day in cdc_vaccine_data.json():
        day_date = day['date']
        day_vaccines_administered_total = int(day['administered'])
        #if 'additional_doses' in day.keys():
        #    day_vaccines_administered_total += int(day['additional_doses'])
        day_vaccines_administered_12plus = day['administered_12plus']
        day_vaccines_administered_18plus = int(day['administered_18plus'])
        #if 'additional_doses_18plus' in day.keys():
        #    day_vaccines_administered_18plus += int(day['additional_doses_18plus'])
        day_vaccines_administered_65plus = int(day['administered_65plus'])
        #if 'additional_doses_65plus' in day.keys():
        #    day_vaccines_administered_65plus += int(day['additional_doses_65plus'])
        first_dose_percent_total = day['administered_dose1_pop_pct']
        first_dose_percent_12plus = day['administered_dose1_recip_2']
        if 'administered_dose1_recip_5pluspop_pct' in day.keys():
            first_dose_percent_5plus = day['administered_dose1_recip_5pluspop_pct']
        else:
            first_dose_percent_5plus = 0
            
        first_dose_percent_18plus = day['administered_dose1_recip_4']
        first_dose_percent_65plus = day['administered_dose1_recip_6']
        fully_vaccinated_total = day['series_complete_pop_pct']
        if 'series_complete_5pluspop_pct' in day.keys():
            fully_vaccinated_5plus = day['series_complete_5pluspop_pct']
        else:
            fully_vaccinated_5plus = 0
            
        fully_vaccinated_12plus = day['series_complete_12pluspop']
        fully_vaccinated_18plus = day['series_complete_18pluspop']
        fully_vaccinated_65plus = day['series_complete_65pluspop']
        
        # Kludge for bad CDC data returns, random days missing values.
        if 'additional_doses_vax_pct' in day.keys():
            booster_percent_total = day['additional_doses_vax_pct']
        else:
            booster_percent_total = 0
        if 'additional_doses_18plus_vax_pct' in day.keys():
            booster_percent_18plus = day['additional_doses_18plus_vax_pct']
        else:
            booster_percent_18plus = 0
        if 'additional_doses_18plus_vax_pct' in day.keys():
            booster_percent_65plus = day['additional_doses_65plus_vax_pct']
        else:
            booster_percent_65plus = 0
        
        bivalent_booster_5plus = 0
        bivalent_booster_12plus = 0
        bivalent_booster_18plus = 0
        bivalent_booster_65plus = 0

        if 'bivalent_booster_5plus_pop_pct' in day.keys():
            bivalent_booster_5plus = day['bivalent_booster_5plus_pop_pct']
        if 'bivalent_booster_12plus_pop_pct' in day.keys():
            bivalent_booster_12plus = day['bivalent_booster_12plus_pop_pct']
        if 'bivalent_booster_18plus_pop_pct' in day.keys():
            bivalent_booster_18plus = day['bivalent_booster_18plus_pop_pct']
        if 'bivalent_booster_65plus_pop_pct' in day.keys():
            bivalent_booster_65plus = day['bivalent_booster_65plus_pop_pct']


        normalized_date = import_date(day_date, add_day=True, cdc=True)

        if normalized_date < IGNORE_DATA_OLDER_THAN or normalized_date > today_formatted:
            continue

        # add day if it doesn't exist
        if normalized_date not in combined_data:
            combined_data[normalized_date] = dict()

        combined_data[normalized_date]['vaccines_administered_total'] = day_vaccines_administered_total
        combined_data[normalized_date]['vaccines_administered_12plus'] = day_vaccines_administered_12plus
        combined_data[normalized_date]['vaccines_administered_18plus'] = day_vaccines_administered_18plus
        combined_data[normalized_date]['vaccines_administered_65plus'] = day_vaccines_administered_65plus
        combined_data[normalized_date]['vaccines_first_dose_percent_total'] = first_dose_percent_total
        combined_data[normalized_date]['vaccines_first_dose_percent_5plus'] = first_dose_percent_5plus
        combined_data[normalized_date]['vaccines_first_dose_percent_12plus'] = first_dose_percent_12plus
        combined_data[normalized_date]['vaccines_first_dose_percent_18plus'] = first_dose_percent_18plus
        combined_data[normalized_date]['vaccines_first_dose_percent_65plus'] = first_dose_percent_65plus
        combined_data[normalized_date]['fully_vaccinated_percent_total'] = fully_vaccinated_total
        combined_data[normalized_date]['fully_vaccinated_percent_5plus'] = fully_vaccinated_5plus
        combined_data[normalized_date]['fully_vaccinated_percent_12plus'] = fully_vaccinated_12plus
        combined_data[normalized_date]['fully_vaccinated_percent_18plus'] = fully_vaccinated_18plus
        combined_data[normalized_date]['fully_vaccinated_percent_65plus'] = fully_vaccinated_65plus
        combined_data[normalized_date]['booster_percent_total'] = booster_percent_total
        combined_data[normalized_date]['booster_percent_18plus'] = booster_percent_18plus
        combined_data[normalized_date]['booster_percent_65plus'] = booster_percent_65plus       
        combined_data[normalized_date]['bivalent_booster_5plus'] = bivalent_booster_5plus       
        combined_data[normalized_date]['bivalent_booster_12plus'] = bivalent_booster_12plus       
        combined_data[normalized_date]['bivalent_booster_18plus'] = bivalent_booster_18plus       
        combined_data[normalized_date]['bivalent_booster_65plus'] = bivalent_booster_65plus       
    
    return combined_data
    
