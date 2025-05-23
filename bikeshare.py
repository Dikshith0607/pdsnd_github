import time
import pandas as pd
import numpy as np
import datetime as dt
import click

CITY_DATA = {
    'chicago': 'chicago.csv',
    'new york city': 'new_york_city.csv',
    'washington': 'washington.csv'
}

months = ('january', 'february', 'march', 'april', 'may', 'june')
weekdays = ('sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday')


def choice(prompt, choices=('y', 'n')):
    """Return a valid input from the user given an array of possible answers."""
    while True:
        user_input = input(prompt).lower().strip()

        if user_input == 'end':
            raise SystemExit

        if ',' not in user_input:
            if user_input in choices:
                return user_input
        else:
            user_input = [i.strip().lower() for i in user_input.split(',')]
            if list(filter(lambda x: x in choices, user_input)) == user_input:
                return user_input

        prompt = ("\nSomething is not right. Please mind the formatting and "
                  "be sure to enter a valid option:\n>")


def get_filters():
    """Asks user to specify a city, month, and day to analyze."""

    print("\n\nLet's explore some US bikeshare data!\n")
    print("Type end at any time if you would like to exit the program.\n")

    while True:
        city = choice("\nFor what city(ies) do you want to select data, "
                      "New York City, Chicago or Washington? Use commas "
                      "to list the names.\n>", CITY_DATA.keys())

        month = choice("\nFrom January to June, for what month(s) do you "
                       "want to filter data? Use commas to list the names.\n>",
                       months)

        day = choice("\nFor what weekday(s) do you want to filter bikeshare "
                     "data? Use commas to list the names.\n>", weekdays)

        confirmation = choice("\nPlease confirm that you would like to apply "
                              "the following filter(s) to the bikeshare data."
                              "\n\n City(ies): {}\n Month(s): {}\n Weekday(s)"
                              ": {}\n\n [y] Yes\n [n] No\n\n>"
                              .format(city, month, day))
        if confirmation == 'y':
            break
        else:
            print("\nLet's try this again!")

    print('-' * 40)
    return city, month, day


def load_data(city, month, day):
    """Loads data for the specified city and filters by month and day if applicable."""
    print("\nThe program is loading the data for the filters of your choice.")
    start_time = time.time()

    if isinstance(city, list):
        df = pd.concat(map(lambda c: pd.read_csv(CITY_DATA[c]), city), sort=True)
        try:
            df = df.reindex(columns=['Unnamed: 0', 'Start Time', 'End Time',
                                     'Trip Duration', 'Start Station',
                                     'End Station', 'User Type', 'Gender',
                                     'Birth Year'])
        except Exception:
            pass
    else:
        df = pd.read_csv(CITY_DATA[city])

    df['Start Time'] = pd.to_datetime(df['Start Time'])
    df['Month'] = df['Start Time'].dt.month
    df['Weekday'] = df['Start Time'].dt.day_name()
    df['Start Hour'] = df['Start Time'].dt.hour

    if isinstance(month, list):
        df = pd.concat([df[df['Month'] == (months.index(m) + 1)] for m in month])
    else:
        df = df[df['Month'] == (months.index(month) + 1)]

    if isinstance(day, list):
        df = pd.concat([df[df['Weekday'] == d.title()] for d in day])
    else:
        df = df[df['Weekday'] == day.title()]

    print("\nThis took {} seconds.".format((time.time() - start_time)))
    print('-' * 40)
    return df


def time_stats(df):
    """Displays statistics on the most frequent times of travel."""

    print('\nCalculating The Most Frequent Times of Travel...\n')
    start_time = time.time()

    most_common_month = df['Month'].mode()[0]
    print('Most common month: ' + months[most_common_month - 1].title())

    most_common_day = df['Weekday'].mode()[0]
    print('Most common day of the week: ' + most_common_day)

    most_common_hour = df['Start Hour'].mode()[0]
    print('Most common start hour: ' + str(most_common_hour))

    print("\nThis took %s seconds." % (time.time() - start_time))
    print('-' * 40)


def station_stats(df):
    """Displays statistics on the most popular stations and trip."""

    print('\nCalculating The Most Popular Stations and Trip...\n')
    start_time = time.time()

    print("Most common start station: " + df['Start Station'].mode()[0])
    print("Most common end station: " + df['End Station'].mode()[0])

    df['Start-End Combination'] = df['Start Station'] + " - " + df['End Station']
    print("Most common trip: " + df['Start-End Combination'].mode()[0])

    print("\nThis took %s seconds." % (time.time() - start_time))
    print('-' * 40)


def trip_duration_stats(df):
    """Displays statistics on the total and average trip duration."""

    print('\nCalculating Trip Duration...\n')
    start_time = time.time()

    total = df['Trip Duration'].sum()
    mean = df['Trip Duration'].mean()

    total_str = f"{int(total // 86400)}d {int((total % 86400) // 3600)}h " \
                f"{int((total % 3600) // 60)}m {int(total % 60)}s"
    mean_str = f"{int(mean // 60)}m {int(mean % 60)}s"

    print("Total travel time: " + total_str)
    print("Mean travel time: " + mean_str)

    print("\nThis took {} seconds.".format((time.time() - start_time)))
    print('-' * 40)


def user_stats(df, city):
    """Displays statistics on bikeshare users."""

    print('\nCalculating User Stats...\n')
    start_time = time.time()

    print("User types:\n", df['User Type'].value_counts().to_string())

    try:
        print("\nGender distribution:\n", df['Gender'].value_counts().to_string())
    except KeyError:
        print("No gender data available for", city.title())

    try:
        print("\nEarliest year of birth:", int(df['Birth Year'].min()))
        print("Most recent year of birth:", int(df['Birth Year'].max()))
        print("Most common year of birth:", int(df['Birth Year'].mode()[0]))
    except:
        print("No birth year data available for", city.title())

    print("\nThis took {} seconds.".format((time.time() - start_time)))
    print('-' * 40)


def raw_data(df, mark_place):
    """Display 5 lines of raw data each time."""

    print("\nYou opted to view raw data.")

    if mark_place > 0:
        if choice("Continue from last place? [y/n] > ") == 'n':
            mark_place = 0

    if mark_place == 0:
        sort_df = choice("\nSort data by: [st] Start Time, [et] End Time, "
                         "[td] Trip Duration, [ss] Start Station, [es] End Station\n> ",
                         ('st', 'et', 'td', 'ss', 'es', ''))

        asc = choice("\nSort order: [a] Ascending, [d] Descending\n> ", ('a', 'd'))

        ascending = asc == 'a'

        sort_map = {
            'st': 'Start Time',
            'et': 'End Time',
            'td': 'Trip Duration',
            'ss': 'Start Station',
            'es': 'End Station'
        }

        if sort_df:
            df = df.sort_values(sort_map[sort_df], ascending=ascending)

    while True:
        print(df.iloc[mark_place:mark_place + 5])
        mark_place += 5
        if choice("Continue printing raw data? [y/n] > ") != 'y':
            break

    return mark_place


def main():
    while True:
        click.clear()
        city, month, day = get_filters()
        df = load_data(city, month, day)
        mark_place = 0

        while True:
            select_data = choice("\nChoose an option:\n"
                                 "[ts] Time Stats\n[ss] Station Stats\n"
                                 "[tds] Trip Duration Stats\n[us] User Stats\n"
                                 "[rd] Raw Data\n[r] Restart\n\n> ",
                                 ('ts', 'ss', 'tds', 'us', 'rd', 'r'))
            click.clear()

            if select_data == 'ts':
                time_stats(df)
            elif select_data == 'ss':
                station_stats(df)
            elif select_data == 'tds':
                trip_duration_stats(df)
            elif select_data == 'us':
                user_stats(df, city)
            elif select_data == 'rd':
                mark_place = raw_data(df, mark_place)
            elif select_data == 'r':
                break

        if choice("Would you like to restart? [y/n] > ") != 'y':
            break


if __name__ == "__main__":
    main()
