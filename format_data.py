from datetime import datetime, date, timedelta

def format_date(date):
    return date.strftime("%Y-%m-%d")

def past_days(num_days, reference_date):
    old_date = reference_date - timedelta(num_days)
    return old_date

def weekly_reference(
    combined_data,
    reference_date,
    infection_data_available = False,
    tests_data_available = False,
    hospitalization_data_available = False,
    vaccine_data_available = False
):
    today_formatted = format_date(reference_date)
    seven_days_ago = format_date(past_days(7, reference_date))
    fourteen_days_ago = format_date(past_days(14, reference_date))
    twentyone_days_ago = format_date(past_days(21, reference_date))
    twentyeight_days_ago = format_date(past_days(28, reference_date))

    cases_today = None
    cases_seven_days_ago = None
    cases_fourteen_days_ago = None
    cases_twentyone_days_ago = None
    cases_twentyeight_days_ago = None

    if infection_data_available:
        cases_today = combined_data[today_formatted]['cases']
        cases_seven_days_ago = combined_data[seven_days_ago]['cases'] if ('cases' in combined_data[seven_days_ago]) else None
        cases_fourteen_days_ago = combined_data[fourteen_days_ago]['cases'] if 'cases' in combined_data[fourteen_days_ago] else None
        cases_twentyone_days_ago = combined_data[twentyone_days_ago]['cases'] if 'cases' in combined_data[twentyone_days_ago] else None
        cases_twentyeight_days_ago = combined_data[twentyeight_days_ago]['cases'] if 'cases' in combined_data[twentyeight_days_ago] else None
    
    tests_today = None
    tests_seven_days_ago = None
    tests_fourteen_days_ago = None
    tests_twentyone_days_ago = None
    tests_twentyeight_days_ago = None

    if tests_data_available:
        tests_today = combined_data[today_formatted]['tested'] if 'tested' in combined_data[today_formatted] else None
        tests_seven_days_ago = combined_data[seven_days_ago]['tested'] if 'tested' in combined_data[seven_days_ago] else None
        tests_fourteen_days_ago = combined_data[fourteen_days_ago]['tested'] if 'tested' in combined_data[fourteen_days_ago] else None
        tests_twentyone_days_ago = combined_data[twentyone_days_ago]['tested'] if 'tested' in combined_data[twentyone_days_ago] else None
        tests_twentyeight_days_ago = combined_data[twentyeight_days_ago]['tested'] if 'tested' in combined_data[twentyeight_days_ago] else None
    
    positivity_today = None
    positivity_seven_days_ago = None
    positivity_fourteen_days_ago = None
    positivity_twentyone_days_ago = None
    positivity_twentyeight_days_ago = None
    if False:
        positivity_today = round((cases_today / tests_today * 100), 2)
        positivity_seven_days_ago = round((cases_seven_days_ago / tests_seven_days_ago * 100), 2)
        positivity_fourteen_days_ago = round((cases_fourteen_days_ago / tests_fourteen_days_ago * 100), 2)
        positivity_twentyone_days_ago = round((cases_twentyone_days_ago / tests_twentyone_days_ago * 100), 2)
        positivity_twentyeight_days_ago = round((cases_twentyeight_days_ago / tests_twentyeight_days_ago * 100), 2)

    ago_prior = "Ago" if (reference_date == date.today()) else "Prior"
    reference_day_of_week = "Today" if (reference_date == date.today()) else reference_date.strftime('%a %b %-d')

    if infection_data_available or tests_data_available:
        week_over_week_reference = f"Week over week reference:  \n"
        if cases_twentyeight_days_ago is not None or tests_twentyeight_days_ago is not None:
            reference_time_string = (f"28 Days {ago_prior}:").rjust(15, '@').replace('@', '&nbsp;')
            week_over_week_reference +=  reference_time_string
        if cases_twentyeight_days_ago is not None:
            week_over_week_reference +=  f" **{cases_twentyeight_days_ago:,}** Cases."
        if tests_twentyeight_days_ago is not None:
            week_over_week_reference +=  f" **{tests_twentyeight_days_ago:,}** Tests."
        if positivity_twentyeight_days_ago is not None:
            week_over_week_reference +=  f" **{positivity_twentyeight_days_ago}%** Positivity."
        if cases_twentyeight_days_ago is not None or tests_twentyeight_days_ago is not None:
             week_over_week_reference +=  "  \n"
        
        if cases_twentyone_days_ago is not None or tests_twentyone_days_ago is not None:
            reference_time_string = (f"21 Days {ago_prior}:").rjust(15, '@').replace('@', '&nbsp;')
            week_over_week_reference +=  reference_time_string
        if cases_twentyone_days_ago is not None:
            week_over_week_reference +=  f" **{cases_twentyone_days_ago:,}** Cases."
        if tests_twentyone_days_ago is not None:
            week_over_week_reference +=  f" **{tests_twentyone_days_ago:,}** Tests."
        if positivity_twentyone_days_ago is not None:
            week_over_week_reference +=  f" **{positivity_twentyone_days_ago}%** Positivity."
        if cases_twentyone_days_ago is not None or tests_twentyone_days_ago is not None:
             week_over_week_reference +=  "  \n"

        if cases_fourteen_days_ago is not None or tests_fourteen_days_ago is not None:
            reference_time_string = (f"14 Days {ago_prior}:").rjust(15, '@').replace('@', '&nbsp;')
            week_over_week_reference +=  reference_time_string
        if cases_fourteen_days_ago is not None:
            week_over_week_reference +=  f" **{cases_fourteen_days_ago:,}** Cases."
        if tests_fourteen_days_ago is not None:
            week_over_week_reference +=  f" **{tests_fourteen_days_ago:,}** Tests."
        if positivity_fourteen_days_ago is not None:
            week_over_week_reference +=  f" **{positivity_fourteen_days_ago}%** Positivity."
        if cases_fourteen_days_ago is not None or tests_fourteen_days_ago is not None:
             week_over_week_reference +=  "  \n"

        if cases_seven_days_ago is not None or tests_seven_days_ago is not None:
            reference_time_string = (f"7 Days {ago_prior}:").rjust(15, '@').replace('@', '&nbsp;')
            week_over_week_reference +=  reference_time_string
        if cases_seven_days_ago is not None:
            week_over_week_reference +=  f" **{cases_seven_days_ago:,}** Cases."
        if tests_seven_days_ago is not None:
            week_over_week_reference +=  f" **{tests_seven_days_ago:,}** Tests."
        if positivity_seven_days_ago is not None:
            week_over_week_reference +=  f" **{positivity_seven_days_ago}%** Positivity."
        if cases_seven_days_ago is not None or tests_seven_days_ago is not None:
             week_over_week_reference +=  "  \n"

        if cases_today is not None or tests_today is not None:
            reference_time_string = (f"{reference_day_of_week}:").rjust(15, '@').replace('@', '&nbsp;')
            week_over_week_reference +=  reference_time_string
        if cases_today is not None:
            week_over_week_reference +=  f" **{cases_today:,}** Cases."
        if tests_today is not None:
            week_over_week_reference +=  f" **{tests_today:,}** Tests."
        if positivity_today is not None:
            week_over_week_reference +=  f" **{positivity_today}%** Positivity."
        if cases_today is not None or tests_today is not None:
             week_over_week_reference +=  "  \n"




        return week_over_week_reference
    else:
        return ""


def weekly_average(combined_data, metric, reference_date):
    total = 0
    for n in range(7):
        processing_date = format_date(past_days(n, reference_date))
        if processing_date not in combined_data:
            continue

        if metric not in  combined_data[processing_date]:
            continue

        total += combined_data[processing_date][metric]
    if total == 0:
        return None
    
    average = total / 7
    return average

def compare_metric(today, last_week):
    if today is None or last_week is None:
        return None
    
    return round((today / last_week - 1) * 100, 2)

def vaccine_average(combined_data, metric, reference_date):
    reference_date_formatted = format_date(reference_date)
    processing_date = format_date(past_days(7, reference_date))
    
    if reference_date_formatted not in combined_data or metric not in combined_data[reference_date_formatted] or processing_date not in combined_data or metric not in combined_data[processing_date]:
        return None

    today_doses = combined_data[reference_date_formatted][metric]
    seven_days_ago_doses = combined_data[processing_date][metric]
    total = int(today_doses) - int(seven_days_ago_doses)
    average = round(total / 7)
    return average

def week_comparison(combined_data, reference_date):
    last_week = past_days(7, reference_date)

    case_7_day_avg_today = weekly_average(combined_data, "cases", reference_date)
    case_7_day_avg_last_week = weekly_average(combined_data, "cases", last_week)
    tested_7_day_avg_today = weekly_average(combined_data, "tested", reference_date)
    tested_7_day_avg_last_week = weekly_average(combined_data, "tested", last_week)
    deaths_7_day_avg_today = weekly_average(combined_data, "deaths", reference_date)
    deaths_7_day_avg_last_week = weekly_average(combined_data, "deaths", last_week)
    hospitalizations_7_day_avg_today = weekly_average(combined_data, "covid_beds", reference_date)
    hospitalizations_7_day_avg_last_week = weekly_average(combined_data, "covid_beds", last_week)
    icu_7_day_avg_today = weekly_average(combined_data, "covid_icu", reference_date)
    icu_7_day_avg_last_week = weekly_average(combined_data, "covid_icu", last_week)
    vent_7_day_avg_today = weekly_average(combined_data, "covid_vent", reference_date)
    vent_7_day_avg_last_week = weekly_average(combined_data, "covid_vent", last_week)
    vaccine_7_day_avg_today = vaccine_average(combined_data, "vaccines_administered_total", reference_date)
    vaccine_7_day_avg_last_week = vaccine_average(combined_data, "vaccines_administered_total", last_week)
    
    case_change = compare_metric(case_7_day_avg_today, case_7_day_avg_last_week)
    tested_change = compare_metric(tested_7_day_avg_today, tested_7_day_avg_last_week)
    death_change = compare_metric(deaths_7_day_avg_today, deaths_7_day_avg_last_week)
    hospitalizations_change = compare_metric(hospitalizations_7_day_avg_today, hospitalizations_7_day_avg_last_week)
    icu_change = compare_metric(icu_7_day_avg_today, icu_7_day_avg_last_week)
    vent_change = compare_metric(vent_7_day_avg_today, vent_7_day_avg_last_week)
    vaccine_change = compare_metric(vaccine_7_day_avg_today, vaccine_7_day_avg_last_week)

    text = "Week over week change in 7-day rolling average:  \n"

    if case_change is not None:
        if case_change > 0:
            text += f"   - New cases up {case_change}%  \n"
        else:
            text += f"   - New cases down {abs(case_change)}%  \n"
    if tested_change is not None:
        if tested_change > 0:
            text += f"   - Testing up {tested_change}%  \n"
        else:
            text += f"   - Testing down {abs(tested_change)}%  \n"
    if death_change is not None:
        if death_change > 0:
            text += f"   - Deaths up {death_change}%  \n"
        else:
            text += f"   - Deaths down {abs(death_change)}%  \n"
    if hospitalizations_7_day_avg_today is not None:
        if hospitalizations_change > 0:
            text += f"   - Hospitalizations up {hospitalizations_change}%  \n"
        else:
            text += f"   - Hospitalizations down {abs(hospitalizations_change)}%  \n"
    if icu_change is not None:
        if icu_change > 0:
            text += f"   - ICU usage up {icu_change}%  \n"
        else:
            text += f"   - ICU usage down {abs(icu_change)}%  \n"
    if vent_change is not None:
        if vent_change > 0:
            text += f"   - Ventilator usage up {vent_change}%  \n"
        else:
            text += f"   - Ventilator usage down {abs(vent_change)}%  \n"
    if vaccine_change is not None:
        if vaccine_change > 0:
            text += f"   - Vaccinations up {vaccine_change}%  \n"
        else:
            text += f"   - Vaccinations down {abs(vaccine_change)}%  \n"

    if case_change is not None or tested_change is not None or death_change is not None or hospitalizations_change is not None or icu_change is not None or vent_change is not None or vaccine_change is not None:
        return text
    
    return ""

def doses_administered(combined_data, metric, reference_date, previous_reference_date):
    today_formatted = format_date(reference_date)

    today_doses = combined_data[today_formatted][metric]
    previous_doses = combined_data[previous_reference_date][metric]

    change = int(today_doses) - int(previous_doses)

    return change
