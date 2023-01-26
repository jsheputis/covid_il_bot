import argparse
import json
import os
import sys
from traceback import print_exc
from format_data import *
from datetime import date, datetime, timezone
from get_data import get_idph_data
import time
import praw
from dateutil import tz

# from praw.util.token_manager import FileTokenManager

USERNAME_ENV_VAR_NAME = "PRAW_USERNAME"
PASSWORD_ENV_VAR_NAME = "PRAW_PASSWORD"

parser = argparse.ArgumentParser(
                    prog = 'CovidILBot',
                    description = 'Retrieves IDPH and CDC Data to post to /r/coronavirusillinois',
        )

parser.add_argument('-p', '--print', action='store_true', default=False)
parser.add_argument('--post-disabled', action='store_true', default=False)
parser.add_argument('--test-post', action='store_true', default=False)
parser.add_argument('--delay', action='store', type=int)
parser.add_argument('--reference-date', action='store', type=lambda s: datetime.strptime(s, '%Y-%m-%d').date())
args = parser.parse_args()

PRINT_OUTPUT = args.print
POST_ENABLED = not args.post_disabled
TEST_POST = args.test_post
REFERENCE_DATE = args.reference_date

REDDIT_INSTANCE = None

if args.delay is not None and args.delay > 0:
    print("Initial delay set for %d seconds" % args.delay)
    time.sleep(args.delay)

def get_reference_date():
    if REFERENCE_DATE is not None:
        return REFERENCE_DATE
    
    return date.today()

# formats date to ISO 8601
def format_date(date):
    return date.strftime("%Y-%m-%d")

def get_reddit_instance():
    global REDDIT_INSTANCE
    if REDDIT_INSTANCE is not None:
        return REDDIT_INSTANCE
    
    credentials_file = open(os.path.join(sys.path[0], "credentials.json"))
    credentials = json.load(credentials_file)

    REDDIT_INSTANCE = praw.Reddit(
        user_agent = "linux:com.jsheputis.covidilbot:v0.2 (by /u/compg318)",
        client_id = credentials["praw_client_id"],
        client_secret = credentials["praw_client_secret"],
        username=os.getenv(USERNAME_ENV_VAR_NAME),
        password=os.getenv(PASSWORD_ENV_VAR_NAME)
    )

    return REDDIT_INSTANCE

# Get today's date and format it how needed
# TODO: Update var name from today for accuracy
today = get_reference_date()
today_formatted = format_date(today)

combined_data = get_idph_data(today)


def get_last_post_date():
    subreddit = 'testingground4bots' if TEST_POST else 'coronavirusillinois'
    # subreddit = 'coronavirusillinois'
    recent_submissions = get_reddit_instance().redditor(os.getenv(USERNAME_ENV_VAR_NAME)).submissions.new(limit=10)
    last_post_date = None
    for recent_submission in recent_submissions:
        if (recent_submission.subreddit == subreddit):
            if last_post_date is None or recent_submission.created_utc > last_post_date:
                last_post_date = recent_submission.created_utc
            
    
    last_post_date_utc = datetime.fromtimestamp(last_post_date, tz=timezone.utc)

    return last_post_date_utc.astimezone(tz=tz.gettz('America/Chicago')).date()

# Instead of handling weekend/holiday logic, let's just go backwards from our reference date until our most recent post date
last_post_date = get_last_post_date()
last_post_date_formatted = format_date(last_post_date)

previous_days_to_process = []
processing_date = today - timedelta(days=1)

while processing_date > last_post_date:
    previous_days_to_process.append(processing_date)
    processing_date = processing_date - timedelta(days=1)

while today_formatted not in combined_data and len(previous_days_to_process) == 0:
    print("Data not available yet, pausing 300 seconds.")
    time.sleep(300)

    today = get_reference_date()
    today_formatted = format_date(today)


# Get the info from today.
todays_data = combined_data[today_formatted] if today_formatted in combined_data else None

infection_data_available = False
hospitalization_data_available = False
vaccine_data_available = False
tests_data_available = False

if todays_data is not None:
    infection_data_available = 'cases' in todays_data
    hospitalization_data_available = 'covid_icu' in todays_data
    vaccine_data_available = 'vaccines_administered_total' in todays_data
    tests_data_available = 'tested' in todays_data

combined_data_keys_sorted = sorted(combined_data.keys(), reverse=True)

def get_previous_infection_date_and_date(reference_date):
    date_formatted = format_date(reference_date)

    previous_infection_date = None
    previous_infection_data = None
    for date_key in combined_data_keys_sorted:
        if date_key != date_formatted and date_key < date_formatted and 'cases' in combined_data[date_key]:
            previous_infection_date = date_key
            previous_infection_data = combined_data[date_key]
            return [previous_infection_date, previous_infection_data]

    return [None, None]

def get_previous_hospitalization_date_and_data(reference_date):
    date_formatted = format_date(reference_date)
    
    previous_hospitalization_date = None
    previous_hospitalization_data = None
    for date_key in combined_data_keys_sorted:
        if date_key != date_formatted and date_key < date_formatted and 'covid_icu' in combined_data[date_key]:
            previous_hospitalization_date = date_key
            previous_hospitalization_data = combined_data[date_key]
            
            return [previous_hospitalization_date, previous_hospitalization_data]
    return [None, None]

def get_previous_vaccine_date_and_data(reference_date):
    date_formatted = format_date(reference_date)
    previous_vaccine_date = None
    previous_vaccine_data = None
    for date_key in combined_data_keys_sorted:
        if date_key != date_formatted and date_key < date_formatted and 'vaccines_administered_total' in combined_data[date_key]:
            previous_vaccine_date = date_key
            previous_vaccine_data = combined_data[date_key]
            return [previous_vaccine_date, previous_vaccine_data]
    return [None, None]

def get_previous_tests_date_and_data(reference_date):
    date_formatted = format_date(reference_date)

    previous_tests_date = None
    previous_tests_data = None
    if tests_data_available:
        for date_key in combined_data_keys_sorted:
            if date_key != date_formatted and date_key < date_formatted and 'tested' in combined_data[date_key]:
                previous_tests_date = date_key
                previous_tests_data = combined_data[date_key]
                
                return [previous_tests_date, previous_tests_data]
    return [None, None]

previous_infection_date_and_data = get_previous_infection_date_and_date(today)
previous_infection_date = previous_infection_date_and_data[0]
previous_infection_data = previous_infection_date_and_data[1]

previous_hospitalization_date_and_data = get_previous_hospitalization_date_and_data(today)
previous_hospitalization_date = previous_hospitalization_date_and_data[0]
previous_hospitalization_data = previous_hospitalization_date_and_data[1]

previous_vaccine_date_and_data = get_previous_vaccine_date_and_data(today)
previous_vaccine_date = previous_vaccine_date_and_data[0]
previous_vaccine_data = previous_vaccine_date_and_data[1]

previous_tests_date_and_data = get_previous_tests_date_and_data(today)
previous_tests_date = previous_tests_date_and_data[0]
previous_tests_data = previous_tests_date_and_data[1]


# positivity = round((new_cases / tests * 100), 2)
positivity = 0


if vaccine_data_available:
    day_vaccines_administered_total = doses_administered(combined_data, 'vaccines_administered_total', today, previous_vaccine_date)
    day_vaccines_administered_12plus = doses_administered(combined_data, 'vaccines_administered_12plus', today, previous_vaccine_date)
    day_vaccines_administered_18plus = doses_administered(combined_data, 'vaccines_administered_18plus', today, previous_vaccine_date)
    day_vaccines_administered_65plus = doses_administered(combined_data, 'vaccines_administered_65plus', today, previous_vaccine_date)

    first_dose_percent_total = todays_data['vaccines_first_dose_percent_total']
    first_dose_percent_5plus = todays_data['vaccines_first_dose_percent_5plus']
    first_dose_percent_12plus = todays_data['vaccines_first_dose_percent_12plus']
    first_dose_percent_18plus = todays_data['vaccines_first_dose_percent_18plus']
    first_dose_percent_65plus = todays_data['vaccines_first_dose_percent_65plus']
    fully_vaccinated_total = todays_data['fully_vaccinated_percent_total']
    fully_vaccinated_5plus = todays_data['fully_vaccinated_percent_5plus']
    fully_vaccinated_12plus = todays_data['fully_vaccinated_percent_12plus']
    fully_vaccinated_18plus = todays_data['fully_vaccinated_percent_18plus']
    fully_vaccinated_65plus = todays_data['fully_vaccinated_percent_65plus']
    booster_percent_total = todays_data['booster_percent_total']
    booster_percent_18plus = todays_data['booster_percent_18plus']
    booster_percent_65plus = todays_data['booster_percent_65plus']
    # vaccine_average_total = vaccine_average(combined_data, 'vaccines_administered_total')

# Generate the title and text based on current data.
title = f"Unofficial Daily Update for {today_formatted}. "
if infection_data_available:
    title += f"{todays_data['cases']:,} New Cases "

if infection_data_available:
    title+="(Cases) "
if tests_data_available:
    title+="(Tests) "
if hospitalization_data_available:
    title+="(Hospitalizations) "
if vaccine_data_available:
    title+="(Vaccines) "

selftext = ""

def generate_infection_data_output(cases, deaths, previous_data_date):
    output = ""
    output += "### Cases \n"
    output += f"There were **{cases:,}** positive cases reported since **{previous_data_date}**. \n\n"
    output += f"There were **{deaths:,}** reported deaths since **{previous_data_date}**.\n\n"

    return output

def generate_test_data_output(tested, positivity_percentage):
    output = ""
    output += "### Tests \n"
    output += f"With {tested:,} tests administered, we have a positivity rate of {positivity_percentage}%.\n\n"

    return output

def generate_hospitalization_data_output(covid_beds, covid_icu, covid_vent):
    output = ""
    output += "### Hospitalizations \n"
    output +=  f"There are **{covid_beds:,}** hospitalizations, with **{covid_icu:,}** in the ICU, and **{covid_vent:,}** ventilators in use.\n\n"

    return output

def generate_vaccine_data_output(
    day_vaccines_administered_total_count,
    fully_vaccinated_total_percentage,
    first_dose_percent_total_percentage,
    booster_percent_total_percentage,
    bivalent_booster_5plus_percentage,
    fully_vaccinated_65plus_percentage,
    first_dose_percent_65plus_percentage,
    booster_percent_65plus_percentage,
    fully_vaccinated_18plus_percentage,
    first_dose_percent_18plus_percentage,
    booster_percent_18plus_percentage,
    fully_vaccinated_12plus_percentage,
    first_dose_percent_12plus_percentage,
    fully_vaccinated_5plus_percentage,
    first_dose_percent_5plus_percentage,
    previous_data_date
):
    output = ""
    output += "### Vaccines \n"
    output += f"*Please note that the vaccine data source has changed from the IDPH to the CDC.*  \n\n"
    output += f"**{day_vaccines_administered_total_count:,}** vaccine doses were administered since **{previous_data_date}**.\n\n"
    output += f"**{fully_vaccinated_total_percentage}%** of the total Illinois population are fully vaccinated, with **{first_dose_percent_total_percentage}%** having received their first dose.  \n**{booster_percent_total_percentage}%** have recieved a booster.  \n**{bivalent_booster_5plus_percentage}%** have recceived a bivalent booster. \n\n"
    output += f"**{fully_vaccinated_65plus_percentage}%** of population age 65+ are fully vaccinated, with **{first_dose_percent_65plus_percentage}%** having received their first dose.  **{booster_percent_65plus_percentage}%** have recieved a booster.  \n"
    output += f"**{fully_vaccinated_18plus_percentage}%** of population age 18+ are fully vaccinated, with **{first_dose_percent_18plus_percentage}%** having received their first dose.  **{booster_percent_18plus_percentage}%** have recieved a booster.  \n"
    output += f"**{fully_vaccinated_12plus_percentage}%** of population age 12+ are fully vaccinated, with **{first_dose_percent_12plus_percentage}%** having received their first dose.  \n"
    output += f"**{fully_vaccinated_5plus_percentage}%** of population age 5+ are fully vaccinated, with **{first_dose_percent_5plus_percentage}%** having received their first dose.  \n\n"

    return output

if infection_data_available:
    selftext += generate_infection_data_output(cases=todays_data['cases'], deaths=todays_data['deaths'], previous_data_date=previous_infection_date)

if tests_data_available:
    selftext += generate_test_data_output(tested=todays_data['tested'], positivity_percentage=positivity)

if hospitalization_data_available:
    selftext += generate_hospitalization_data_output(covid_beds=todays_data['covid_beds'], covid_icu=todays_data['covid_icu'], covid_vent=todays_data['covid_vent'])

if vaccine_data_available:
    selftext += generate_vaccine_data_output(
        day_vaccines_administered_total_count = day_vaccines_administered_total,
        fully_vaccinated_total_percentage = fully_vaccinated_total,
        first_dose_percent_total_percentage = first_dose_percent_total,
        booster_percent_total_percentage = booster_percent_total,
        bivalent_booster_5plus_percentage = todays_data['bivalent_booster_5plus'],
        fully_vaccinated_65plus_percentage = fully_vaccinated_65plus,
        first_dose_percent_65plus_percentage = first_dose_percent_65plus,
        booster_percent_65plus_percentage = booster_percent_65plus,
        fully_vaccinated_18plus_percentage = fully_vaccinated_18plus,
        first_dose_percent_18plus_percentage = first_dose_percent_18plus,
        booster_percent_18plus_percentage = booster_percent_18plus,
        fully_vaccinated_12plus_percentage = fully_vaccinated_12plus,
        first_dose_percent_12plus_percentage = first_dose_percent_12plus,
        fully_vaccinated_5plus_percentage = fully_vaccinated_5plus,
        first_dose_percent_5plus_percentage = first_dose_percent_5plus,
        previous_data_date = previous_vaccine_date
    )


# TODO: Wrapping with exception handling as is work in progress, any unknown failure scenario will just surpress weekly reference/comparison data
weekly_reference_output = ""
try:
    weekly_reference_output += f"{weekly_reference(combined_data, reference_date=today, infection_data_available=infection_data_available, tests_data_available=tests_data_available, hospitalization_data_available=hospitalization_data_available, vaccine_data_available=vaccine_data_available)}"
    if weekly_reference_output:
        weekly_reference_output += "\n\n"
except Exception as e:
    print("Error in weekly reference report [{}]".format(e))
    print_exc()
weekly_comparison_output = ""
try:
    weekly_comparison_output = ""
    #weekly_comparison_output += f"{week_comparison(combined_data, reference_date=today)}"
    if weekly_comparison_output:
        weekly_comparison_output += "\n\n"
except Exception as e:
    print("Error in weekly comparison report[{}]".format(e))
    print_exc()

if weekly_reference_output or weekly_comparison_output:
    selftext += "### Weekly "
    if weekly_reference_output:
        selftext += "Reference "
    if weekly_reference_output and weekly_comparison_output:
        selftext += "and "
    if weekly_comparison_output:
        selftext += "Comparison "
    selftext += "\n"
    selftext += weekly_reference_output
    selftext += weekly_comparison_output

# TODO: Handle scenario when previous_sunday and previous_saturday are the same values to avoid confusing messaging -- may not be an issue but need to see data output first
# i.e. Sunday: XXXX since 2022-12-31
#      Saturday: YYYY since 2022-12-31
def get_prior_day_output_data(prior_day_date):
    prior_day_date_formatted = format_date(prior_day_date)
    prior_day_data = combined_data[prior_day_date_formatted] if prior_day_date_formatted in combined_data else None

    if prior_day_data is None:
        return ""
    
    # TODO: Cleanup unused vars after finalizing output, currently setting all data for ease of manipulating report output
    prior_day_infection_data_available = 'cases' in prior_day_data
    prior_day_hospitalization_data_available = 'covid_icu' in prior_day_data
    prior_day_vaccine_data_available = 'vaccines_administered_total' in prior_day_data
    prior_day_tests_data_available = 'tested' in prior_day_data

    prior_day_previous_infection_date_and_data = get_previous_infection_date_and_date(prior_day_date)
    prior_day_previous_infection_date = prior_day_previous_infection_date_and_data[0]
    prior_day_previous_infection_data = prior_day_previous_infection_date_and_data[1]

    prior_day_previous_hospitalization_date_and_data = get_previous_hospitalization_date_and_data(prior_day_date)
    prior_day_previous_hospitalization_date = prior_day_previous_hospitalization_date_and_data[0]
    prior_day_previous_hospitalization_data = prior_day_previous_hospitalization_date_and_data[1]

    prior_day_previous_vaccine_date_and_data = get_previous_vaccine_date_and_data(prior_day_date)
    prior_day_previous_vaccine_date = prior_day_previous_vaccine_date_and_data[0]
    prior_day_previous_vaccine_data = prior_day_previous_vaccine_date_and_data[1]

    prior_day_previous_tests_date_and_data = get_previous_tests_date_and_data(prior_day_date)
    prior_day_previous_tests_date = prior_day_previous_tests_date_and_data[0]
    prior_day_previous_tests_data = prior_day_previous_tests_date_and_data[1]

    if prior_day_vaccine_data_available:
        prior_day_day_vaccines_administered_total = doses_administered(combined_data, 'vaccines_administered_total', prior_day_date, prior_day_previous_vaccine_date)
        prior_day_day_vaccines_administered_12plus = doses_administered(combined_data, 'vaccines_administered_12plus', prior_day_date, prior_day_previous_vaccine_date)
        prior_day_day_vaccines_administered_18plus = doses_administered(combined_data, 'vaccines_administered_18plus', prior_day_date, prior_day_previous_vaccine_date)
        prior_day_day_vaccines_administered_65plus = doses_administered(combined_data, 'vaccines_administered_65plus', prior_day_date, prior_day_previous_vaccine_date)
        
        prior_day_first_dose_percent_total = prior_day_data['vaccines_first_dose_percent_total']
        prior_day_first_dose_percent_5plus = prior_day_data['vaccines_first_dose_percent_5plus']
        prior_day_first_dose_percent_12plus = prior_day_data['vaccines_first_dose_percent_12plus']
        prior_day_first_dose_percent_18plus = prior_day_data['vaccines_first_dose_percent_18plus']
        prior_day_first_dose_percent_65plus = prior_day_data['vaccines_first_dose_percent_65plus']
        prior_day_fully_vaccinated_total = prior_day_data['fully_vaccinated_percent_total']
        prior_day_fully_vaccinated_5plus = prior_day_data['fully_vaccinated_percent_5plus']
        prior_day_fully_vaccinated_12plus = prior_day_data['fully_vaccinated_percent_12plus']
        prior_day_fully_vaccinated_18plus = prior_day_data['fully_vaccinated_percent_18plus']
        prior_day_fully_vaccinated_65plus = prior_day_data['fully_vaccinated_percent_65plus']
        prior_day_booster_percent_total = prior_day_data['booster_percent_total']
        prior_day_booster_percent_18plus = prior_day_data['booster_percent_18plus']
        prior_day_booster_percent_65plus = prior_day_data['booster_percent_65plus']

    output = "  \n\n ------------------ \n\n"
    output += f"## {prior_day_date.strftime('%A')} - {prior_day_date_formatted}  \n"
    if prior_day_infection_data_available:
        output += generate_infection_data_output(cases=prior_day_data['cases'], deaths=prior_day_data['deaths'], previous_data_date=prior_day_previous_infection_date)

    if prior_day_tests_data_available:
        output += generate_test_data_output(tested=prior_day_data['tested'], positivity_percentage=None)

    if prior_day_hospitalization_data_available:
        output += generate_hospitalization_data_output(covid_beds=prior_day_data['covid_beds'], covid_icu=prior_day_data['covid_icu'], covid_vent=prior_day_data['covid_vent'])

    if prior_day_vaccine_data_available:
        output += generate_vaccine_data_output(
            day_vaccines_administered_total_count = prior_day_day_vaccines_administered_total,
            fully_vaccinated_total_percentage = prior_day_fully_vaccinated_total,
            first_dose_percent_total_percentage = prior_day_first_dose_percent_total,
            booster_percent_total_percentage = prior_day_booster_percent_total,
            bivalent_booster_5plus_percentage = prior_day_data['bivalent_booster_5plus'],
            fully_vaccinated_65plus_percentage = prior_day_fully_vaccinated_65plus,
            first_dose_percent_65plus_percentage = prior_day_first_dose_percent_65plus,
            booster_percent_65plus_percentage = prior_day_booster_percent_65plus,
            fully_vaccinated_18plus_percentage = prior_day_fully_vaccinated_18plus,
            first_dose_percent_18plus_percentage = prior_day_first_dose_percent_18plus,
            booster_percent_18plus_percentage = prior_day_booster_percent_18plus,
            fully_vaccinated_12plus_percentage = prior_day_fully_vaccinated_12plus,
            first_dose_percent_12plus_percentage = prior_day_first_dose_percent_12plus,
            fully_vaccinated_5plus_percentage = prior_day_fully_vaccinated_5plus,
            first_dose_percent_5plus_percentage = prior_day_first_dose_percent_5plus,
            previous_data_date = prior_day_previous_vaccine_date
        )

    weekly_reference_output = ""
    try:
        weekly_reference_output += f"{weekly_reference(combined_data, reference_date=prior_day_date, infection_data_available=prior_day_infection_data_available, tests_data_available=prior_day_tests_data_available, hospitalization_data_available=prior_day_hospitalization_data_available, vaccine_data_available=prior_day_vaccine_data_available)}"
        if weekly_reference_output:
            weekly_reference_output += "\n\n"
    except Exception as e:
        print("Error in weekly reference report [{}]".format(e))
        print_exc()
    weekly_comparison_output = ""
    try:
        # weekly_comparison_output += f"{week_comparison(combined_data, reference_date=prior_day_date)}"
        weekly_comparison_output = ""
        if weekly_comparison_output:
            weekly_comparison_output += "\n\n"
    except Exception as e:
        print("Error in weekly comparison report[{}]".format(e))
        print_exc()

    if weekly_reference_output or weekly_comparison_output:
        output += "### Weekly  "
        if weekly_reference_output:
            output += "Reference "
        if weekly_reference_output and weekly_comparison_output:
            output += "and "
        if weekly_comparison_output:
            output += "Comparison "
        output += "\n"
        output += weekly_reference_output
        output += weekly_comparison_output


    return output


for previous_day_to_process in previous_days_to_process:
    selftext += get_prior_day_output_data(previous_day_to_process)



selftext += (
        "  \n\n ------------------ \n\n  "
        "This post was automatically generated based on the latest data from the IDPH and CDC websites.  \n"
        "^(Source code is available at https://github.com/jsheputis/covid_il_bot)")


if PRINT_OUTPUT:
    print("##" + title + "\n\n  ")
    print("\n\n---------------------------------------------------------------------------------------------------------------------------\n\n  ")
    print(selftext)

if POST_ENABLED:
    reddit = get_reddit_instance()

    reddit.validate_on_submit = True

    if TEST_POST:
        post = reddit.subreddit("testingground4bots").submit(title, selftext=selftext)
    else:
        post = reddit.subreddit("coronavirusillinois").submit(title, selftext=selftext, flair_id="4be3f066-cf71-11eb-95ff-0e28526b1d53")

