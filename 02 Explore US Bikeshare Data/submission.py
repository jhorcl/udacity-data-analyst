import os
import sys
import calendar
import pandas as pd
import argparse as ap
from timeit import default_timer as timer


def timed_calculation(function_name, *args):
    """Calculates a statistic and measures the time it took to do it.

    Args:
        function_name (function): the function to call
        *args: Variable length argument list which is passed to the called
               function
    Returns:
        tuple: a tuple with the result and the time the calculation took
    """
    start_time = timer()
    result = function_name(*args)
    return (result, timer() - start_time)
    # ---------------------------------------------------- timed_calculation()


def get_most_common_value(data_frame, field):
    """Calculates the most common value (mode) of a field in a given DataFrame.

    Args:
        data_frame (DataFrame):  the Pandas DataFrame to analyze
        field (string): the field to calculate the modal from

    Returns:
        Series: the most common value of the field
    """
    return data_frame[field].mode()[0]
    # ------------------------------------------------ get_most_common_value()


def get_total(data_frame, field):
    """Calculates the sum of a given field in a given DataFrame.

    Args:
        data_frame (DataFrame): the Pandas DataFrame to analyze
        field (string): the field to calculate the sum of

    Returns:
        Series: the sum of the given field
    """
    return data_frame[field].sum()
    # ------------------------------------------------------------ get_total()


def get_average(data_frame, field):
    """Calculates the mean of a given field in a given DataFrame.

    Args:
        data_frame (DataFrame): the Pandas DataFrame to analyze
        field (string): the field to calculate the mean of

    Returns:
        Series: the mean of the given field
    """
    return data_frame[field].mean()
    # ---------------------------------------------------------  get_average()


def get_value_counts(data_frame, field):
    """Calculates the value count of a given field in a given DataFrame.

    Args:
        data_frame (DataFrame): the Pandas DataFrame to analyze
        field (string): the field to calculate the values of

    Returns:
        Series: a Pandas Series representing the count of distinct values
    """
    return data_frame[field].value_counts()
    # ----------------------------------------------------- get_value_counts()


def get_ratio(data_frame, field):
    """Calculates the ratio of the values of a given field of a DataFrame.

    Args:
        data_frame (DataFrame): a Pandas DataFrame to analyze
        field (string): the field to calculate the values of

    Returns:
        Series: Pandas Series representing the count of distinct values as
                ratio
    """
    return data_frame[field].value_counts(normalize=True) * 100
    # ------------------------------------------------------------ get_ratio()


def get_nlargest_by_group(data_frame, field_list, top_n):
    """Calculates the most common value of a field combination by
    grouping the dataframe by a given list of fields, and calculating the
    largest group.

    Args:
        data_frame (DataFrame): the Pandas DataFrame to group and analyze
        field_list (list): the list of fields to group by
        top_n (int) the number for the top n results

    Returns:
        DataFrame: The DataFrame containing the Top N result
    """
    return data_frame.groupby(field_list).size().nlargest(top_n).reset_index(
        name='count')
    # ------------------------------------------------ get_nlargest_by_group()


def get_nsmallest_by_group(data_frame, field_list, top_n):
    """Calculates the least common value of a field combination by
    grouping the dataframe by a given list of fields, and calculating the
    smallest group.

    Args:
        data_frame (DataFrame): the Pandas DataFrame to group and analyze
        field_list (list): the list of fields to group by
        top_n (int) the number for the top n results of the smallest group

    Returns:
        DataFrame: The DataFrame containing the Top N result
    """
    return data_frame.groupby(field_list).size().nsmallest(top_n).reset_index(
        name='count')
    # ----------------------------------------------- get_nsmallest_by_group()


def get_max_of_group(data_frame, field_list, group_name, group_value):
    """Groups a DataFrame by a list of fields, creates a new column with the
    count of values per group and returns the maximum value of given field in
    a given group.

    Args:
        data_frame (DataFrame): the Pandas DataFrame to group and analyze
        field_list (list): the list of fields to group by
        group_name (String): the name of the Group the max value is searched in
        group_value (Object): the value the Group should be filtered by

    Returns:
        the maximum value in the given group
    """
    grouped_df = data_frame.groupby(field_list).size().reset_index(
        name='count')
    group_df = grouped_df[grouped_df[group_name] == group_value].reset_index()
    max_index = get_max_index(group_df, 'count')
    return get_row_by_index(group_df, max_index)
    # ----------------------------------------------------- get_max_of_group()


def get_min(data_frame, field):
    """Calculates the minimum value of a given field in a given DataFrame.

    Args:
        data_frame (DataFrame): the Pandas DataFrame to analyze
        field (string): the field to calculate the values of

    Returns:
        Series: the minimum value of the field
    """
    return data_frame[field].min()
    # -------------------------------------------------------------- get_min()


def get_max(data_frame, field):
    """Calculates the maximum value of a given field in a given DataFrame.

    Args:
        data_frame (DataFrame): the Pandas DataFrame to analyze
        field (string): the field to calculate the values of

    Returns:
        Series: the maximum value of the field
    """
    return data_frame[field].max()
    # -------------------------------------------------------------- get_max()


def get_min_index(data_frame, field):
    """Finds the index of the smallest value of a given field in a DataFrame.

    Args:
        data_frame (DataFrame): the Pandas DataFrame to analyze
        field (string): the field to find the smallest field of

    Returns:
        Series: the index of the smallest value of the field
    """
    return data_frame[field].idxmin()
    # -------------------------------------------------------- get_min_index()


def get_max_index(data_frame, field):
    """Finds the index of the largest value of a given field in a DataFrame.

    Args:
        data_frame (DataFrame): the Pandas DataFrame to analyze
        field (string): the field to calculate the largest value in

    Returns:
        Series: the index of the maximum value of the field
    """
    return data_frame[field].idxmax()
    # -------------------------------------------------------- get_max_index()


def get_row_by_index(data_frame, index):
    """Returns all columns of a DataFrame for a given index.

    Args:
        data_frame (DataFrame): the Pandas DataFrame to use
        index (int): the index to access the DataFrame

    Returns:
        Series: a Pandas Series containing all cols at the given index
    """
    return data_frame.iloc[index]
    # ----------------------------------------------------- get_row_by_index()


def load_data(options):
    """Loads data for the specified city and filters by month and day if
    applicable.

    Args:
        options (dict): dictionary holding filters and user choices

    Returns:
        DataFrame containing city data filtered by month and day if applicable

    `options` must contain
        - city_of_interest: tuple containing [city_name][file_name]
        - filter_type: String holding one of 'Month', 'Day', 'Both' or None
        - month_of_interest: int holding the number of the month (1 = Jan)
        - day_of_interest: int holding the weekday (0 = Mon)
    """

    # load data file into a dataframe
    # as we know the format in advance we will convert columns 1 and 2 to
    # datetime and afterwards drop the first column to remove the unnamed
    # column that exists in the csv files
    df = pd.read_csv(options['city_of_interest']['file'], parse_dates=[1, 2])
    df = df.drop(df.columns[0], axis=1)

    # create new columns having month, weekday, and start hour
    df['Month'] = df['Start Time'].dt.month
    df['Weekday'] = df['Start Time'].dt.weekday
    df['Start Hour'] = df['Start Time'].dt.hour
    df['End Hour'] = df['End Time'].dt.hour

    # apply the filters if applicable
    if options['filter_type'] is not None:
        if (options['filter_type'] == 'Month'
                or options['filter_type'] == 'Both'):
            df = df[df['Month'] == options['month_of_interest']].reset_index()
        if (options['filter_type'] == 'Day'
                or options['filter_type'] == 'Both'):
            df = df[df['Weekday'] == options['day_of_interest']].reset_index()

    return df
    # ------------------------------------------------------------ load_data()


def analyze(options):
    """Calculates statistics base on the given options.

    Args:
        options (Dict): a dictionary holding at least the keys
        - city_of_interest (Tuple): Holds the name of the City and the
                                    name of the CSV file to analyze.
        - filter_type (String): One of None, Month, Day or Both
                                Specifies the filter wanted.
        - month_of_interest (int): The number of the Month to analyze where
                                   January = 1
        - day_of_interest (int): The weekday to analyze where Monday = 0
        - interactive (bool): If true this function asks the user to restart
                              the process
    """

    print('\nStart analyzing your data ...')

    # first load the data into a data frame
    city_df, total_time = timed_calculation(load_data, options)
    print('\n({:3.4f}s) Loaded file {}.'.format(
        total_time, options['city_of_interest']['file']))

    # -------------------------------
    # #1 Popular times of travel
    #
    # If we filter by month and/or day it does not make sense to
    # display the most commont month and/or day. So only calculate
    # the needed statistics based on the filter the user choosed.

    # Do we need to display the month? If we filter by day or do not
    # filter at all, we calculate it.
    if (options['filter_type'] is None or options['filter_type'] == 'Day'):
        most_common_month, total_time = timed_calculation(
            get_most_common_value, city_df, 'Month')
        print(
            '({:3.4f}s) The most popular month for traveling is "{}".'.format(
                total_time, calendar.month_name[most_common_month]))

    # Same logic applies to the day. If we filter by day anyway we need
    # not to display that data.
    if (options['filter_type'] is None or options['filter_type'] == 'Month'):
        most_common_weekday, total_time = timed_calculation(
            get_most_common_value, city_df, 'Weekday')
        print('({:3.4f}s) The most popular weekday for traveling is "{}".'.
              format(total_time, calendar.day_name[most_common_weekday]))

    # The most popular hour is calculated every time.
    most_common_hour, total_time = timed_calculation(get_most_common_value,
                                                     city_df, 'Start Hour')
    print('({:3.4f}s) The most popular hour for traveling is "{}".'.format(
        total_time, most_common_hour))

    # The most popular return hour
    most_common_hour, total_time = timed_calculation(get_most_common_value,
                                                     city_df, 'End Hour')
    print('({:3.4f}s) The most popular return hour is "{}".'.format(
        total_time, most_common_hour))

    # ------------------------------------------------
    # 2 Popular and unpopular stations and trips
    #
    # most common start station
    most_common_start_station, total_time = timed_calculation(
        get_most_common_value, city_df, 'Start Station')
    print('({:3.4f}s) The most popular start station is "{}".'.format(
        total_time, most_common_start_station))

    # most common end station
    most_common_end_station, total_time = timed_calculation(
        get_most_common_value, city_df, 'End Station')
    print('({:3.4f}s) The most popular end station is "{}".'.format(
        total_time, most_common_end_station))

    # most common trip from start to end (i.e., most frequent combination
    # of start station and end station)
    most_common_trip, total_time = timed_calculation(
        get_nlargest_by_group, city_df, ['Start Station', 'End Station'], 1)
    print(
        '({:3.4f}s) The most popular trip from start to end is from "{}" '
        ' to "{}", which was taken {} times.'.format(
            total_time, most_common_trip['Start Station'][0],
            most_common_trip['End Station'][0], most_common_trip['count'][0]))

    # Print one of the most unpopular trips - there is a high probability that
    # there are more than one trips that are taken only 1 times. But print
    # that anyway.
    most_unpopular_trip, total_time = timed_calculation(
        get_nsmallest_by_group, city_df, ['Start Station', 'End Station'], 1)
    print(
        '({:3.4f}s) One of the most unpopular trips from start to end is from '
        '"{}" to "{}", which was only taken {} times.'.format(
            total_time, most_unpopular_trip['Start Station'][0],
            most_unpopular_trip['End Station'][0],
            most_unpopular_trip['count'][0]))

    # ---------------------------------------------------
    # 3 Trip duration
    # total travel time
    total_trip_duration, total_time = timed_calculation(
        get_total, city_df, 'Trip Duration')
    print('({:3.4f}s) The total travel time is {}.'.format(
        total_time, str(pd.to_timedelta(total_trip_duration, unit='s'))))

    # average travel time
    average_trip_duration, total_time = timed_calculation(
        get_average, city_df, 'Trip Duration')
    print('({:3.4f}s) The average travel time is {}.'.format(
        total_time, str(pd.to_timedelta(average_trip_duration, unit='s'))))

    # shortest trip
    shortest_trip_index, total_time1 = timed_calculation(
        get_min_index, city_df, 'Trip Duration')
    shortest_trip, total_time2 = timed_calculation(get_row_by_index, city_df,
                                                   shortest_trip_index)
    print('({:3.4f}s) The shortest trip is {}. Trip details are:'.format(
        total_time1 + total_time2,
        str(pd.to_timedelta(shortest_trip['Trip Duration'], unit='s'))))
    print(shortest_trip.to_string())

    # longest trip
    longest_trip_index, total_time1 = timed_calculation(
        get_max_index, city_df, 'Trip Duration')
    longest_trip, total_time2 = timed_calculation(get_row_by_index, city_df,
                                                  longest_trip_index)
    print('({:3.4f}s) The longest trip is {}. Trip details are:'.format(
        total_time1 + total_time2,
        str(pd.to_timedelta(longest_trip['Trip Duration'], unit='s'))))
    print(longest_trip.to_string())

    # -------------------------------
    # 4 User info
    # counts of each user type
    users_breakdown, total_time = timed_calculation(get_value_counts, city_df,
                                                    'User Type')
    print('({:3.4f}s) The different users are:'.format(total_time))
    for i, v in users_breakdown.items():
        print('{}\t{}'.format(i, v))

    # raio of user type
    users_ratio, total_time = timed_calculation(get_ratio, city_df,
                                                'User Type')
    print('({:3.4f}s) This is a ratio of:'.format(total_time))
    for i, v in users_ratio.items():
        print('{}\t{:3.2f} %'.format(i, v))

    if 'Gender' in city_df:
        # counts of each gender (only available for NYC and Chicago)
        gender_breakdown, total_time = timed_calculation(
            get_value_counts, city_df, 'Gender')
        print('({:3.4f}s) Differences of gender is:'.format(total_time))
        for i, v in gender_breakdown.items():
            print('{}\t{}'.format(i, v))

        # ratio of gender
        gender_ratio, total_time = timed_calculation(get_ratio, city_df,
                                                     'Gender')
        print('({:3.4f}s) The gender ratio is:'.format(total_time))
        for i, v in gender_ratio.items():
            print('{}\t{:3.2f} %'.format(i, v))

        # when do men and women most often start
        max_of_group, total_time = timed_calculation(
            get_max_of_group, city_df, ['Gender', 'Start Station'], 'Gender',
            'Male')
        print('({:3.4f}s) Men most often start from "{}" ({} Times).'.format(
            total_time, max_of_group['Start Station'], max_of_group['count']))
        max_of_group, total_time = timed_calculation(
            get_max_of_group, city_df, ['Gender', 'Start Station'], 'Gender',
            'Female')
        print('({:3.4f}s) Women most often start from "{}" ({} Times).'.format(
            total_time, max_of_group['Start Station'], max_of_group['count']))

        # what timeframe per gender
        max_of_group, total_time = timed_calculation(get_max_of_group, city_df,
                                                     ['Gender', 'Start Hour'],
                                                     'Gender', 'Male')
        print('({:3.4f}s) Men most often start at "{}" o\'clock ({} Times).'.
              format(total_time, max_of_group['Start Hour'],
                     max_of_group['count']))
        max_of_group, total_time = timed_calculation(get_max_of_group, city_df,
                                                     ['Gender', 'Start Hour'],
                                                     'Gender', 'Female')
        print('({:3.4f}s) Women most often start at "{}" o\'clock ({} Times).'.
              format(total_time, max_of_group['Start Hour'],
                     max_of_group['count']))

    # earliest, most recent, most common year of birth (only available for
    # NYC and Chicago)
    if 'Birth Year' in city_df:
        # earliest
        youngest, total_time = timed_calculation(get_max, city_df,
                                                 'Birth Year')
        print('({:3.4f}s) The yougest driver was born in {:4.0f}.'.format(
            total_time, youngest))
        # most recent
        oldest, total_time = timed_calculation(get_min, city_df, 'Birth Year')
        print('({:3.4f}s) The oldest was born in {:4.0f}.'.format(
            total_time, oldest))
        # most common
        most_common, total_time = timed_calculation(get_most_common_value,
                                                    city_df, 'Birth Year')
        print('({:3.4f}s) The most common year of birth is {:4.0f}.'.format(
            total_time, most_common))

    if options['interactive']:
        # start over or quit
        try:
            input('\nTo restart, press enter. To quit, press "Ctrl-C".')
        except KeyboardInterrupt:
            raise
    # ---------------------------------------------------------------analyze()


def show_menu():
    """show_menue is used to show a menu on screen until the user quits the
    script by pressing Ctrl+C or Ctrl+D. Ctrl+C is the official way to
    quit the script, Ctrl+D is excepted as well.

    All functions used to get input by the user are implemented as nested
    functions to implement a better separation of interactive and non-
    interactive incovation.
    """

    def change_filter(options):
        """Offers a menu to change the filter wanted."""

        print('Please choose a filter or press return to discard\nthe change:')

        # show a list of valid filters
        for filter_type in options['allowed_filters']:
            print('({}) {}'.format(
                options['allowed_filters'].index(filter_type) + 1,
                filter_type))

        # get the input and check whether it is a valid choice
        while True:
            user_choice = input('-> ')
            # return pressed
            if len(user_choice) == 0:
                break
            else:
                try:
                    filter_choosen = int(user_choice)
                except ValueError:
                    print('Please enter a number!')
                    continue
                else:
                    filter_choosen -= 1
                    if 0 <= filter_choosen < len(options['allowed_filters']):
                        options['filter_type'] = options['allowed_filters'][
                            filter_choosen]
                        # after changing the filter we call the
                        # function to change the filter value immediatly
                        if options['allowed_filters'][
                                filter_choosen] == 'None':
                            options['filter_type'] = None
                            break
                        if options['allowed_filters'][
                                filter_choosen] == 'Month':
                            change_month(options)
                            break
                        elif options['allowed_filters'][
                                filter_choosen] == 'Day':
                            change_day(options)
                            break
                        elif options['allowed_filters'][
                                filter_choosen] == 'Both':
                            change_month(options)
                            change_day(options)
                            break
                    else:
                        print('Please enter a valid number shown above!')
                        continue
        # ---------------------------------------------------- change_filter()

    def change_city(options):
        """Offers a menu to change the city to analyze data for."""

        print('Please choose a city or press return to discard\nthe change:')

        # show a list of valid cities
        for city_dict in city_data:
            print('({}) {}'.format(
                city_data.index(city_dict) + 1, city_dict['name']))

        # validate the choice of the user
        while True:
            user_choice = input('-> ')
            # return was pressed
            if len(user_choice) == 0:
                break
            else:
                try:
                    city_choosen = int(user_choice)
                except ValueError:
                    print('Please enter a number!')
                    continue
                else:
                    city_choosen -= 1
                    if 0 <= city_choosen < len(city_data):
                        options['city_of_interest'] = city_data[city_choosen]
                        break
                    else:
                        print('Please enter a valid number shown above!')
                        continue
        # ------------------------------------------------------ change_city()

    def change_month(options):
        """Offers a menu to change the month to filter."""

        print('Please choose a month or press return to choose '
              '{}:'.format(calendar.month_name[options['month_of_interest']]))

        # show a list of allowed months
        for month in options['allowed_months']:
            print('({}) {}'.format(month, calendar.month_name[month]))

        # and loop until a valid choice was made
        while True:
            user_choice = input('-> ')
            if len(user_choice) == 0:
                break
            else:
                try:
                    month_choosen = int(user_choice)
                except ValueError:
                    print('Please enter a number!')
                    continue
                else:
                    if month_choosen in options['allowed_months']:
                        options['month_of_interest'] = month_choosen
                        break
                    else:
                        print('Please enter a valid number shown above!')
                        continue
        # ----------------------------------------------------- change_month()

    def change_day(options):
        """Offers a menu to change the day to filter."""

        print('Please choose a day or press return to choose '
              '{}:'.format(calendar.day_name[options['day_of_interest']]))

        # show allowed days as menu
        for day in options['allowed_days']:
            print('({}) {}'.format(day + 1, calendar.day_name[day]))

        # loop until a valid choice was made
        while True:
            user_choice = input('-> ')
            # return was pressed
            if len(user_choice) == 0:
                break
            else:
                try:
                    day_choosen = int(user_choice)
                except ValueError:
                    print('Please enter a number!')
                    continue
                else:
                    day_choosen -= 1
                    if day_choosen in options['allowed_days']:
                        options['day_of_interest'] = day_choosen
                        break
                    else:
                        print('Please enter a valid number shown above!')
                        continue
        # ------------------------------------------------------- change_day()

    def get_user_input():
        """Function to print the menu on Screen and pass back the input.
        It's implemented as inner function because all interactive parts
        should only be available if this file is used as script.

        Returns:
            A function to change either:
            - city    = change city to analyze
            - filter  = change filter used
            - month   = change month to analyze
            - day     = change day to analyze
            or to start analyzing the data.
        """

        # print the menu on screen
        # header
        os.system('cls' if os.name == 'nt' else 'clear')
        print('Hello! Let\'s explore some US bikeshare data!')
        print('--------------------------------------------')

        # current choices
        print('(1) City: {} (File: {})'.format(
            options['city_of_interest']['name'],
            options['city_of_interest']['file']))

        if options['filter_type'] is None:
            print('(2) Filter: None')
        else:
            print('(2) Filter: {}'.format(options['filter_type']))

            # Month and day are stored as integers for easier usage
            # of datetime module later - so use calendar module to display
            # friendly names
            if options['filter_type'] == 'Both':
                print('(3) Month: {}'.format(
                    calendar.month_name[options['month_of_interest']]))
                print('(4) Day: {}'.format(
                    calendar.day_name[options['day_of_interest']]))
            elif options['filter_type'] == 'Day':
                print('(3) Day: {}'.format(
                    calendar.day_name[options['day_of_interest']]))
            else:
                print('(3) Month: {}'.format(
                    calendar.month_name[options['month_of_interest']]))

        # footer
        print('------------------')
        print("Please press 'Enter' to analyze the shown City\nusing "
              "the given filter or select one of the\noptions to "
              "change it's value. Use CTRL+C to quit")
        while True:
            user_choice = input('-> ')
            if len(user_choice) == 0:
                return analyze
            else:
                try:
                    option_to_change = int(user_choice)
                except ValueError:
                    print('Please enter a number!')
                    continue
                else:
                    if option_to_change == 1:
                        return change_city
                    elif option_to_change == 2:
                        return change_filter
                    elif options['filter_type'] == "Both":
                        if option_to_change == 3:
                            return change_month
                        else:
                            return change_day
                    elif (options['filter_type'] == "Month"
                          and option_to_change == 3):
                        return change_month
                    elif (options['filter_type'] == "Day"
                          and option_to_change == 3):
                        return change_day
                    else:
                        print('Please enter a valid number shown above!')
                        continue

        # --------------------------------------------------- get_user_input()

    # show a menu until Ctrl+C or Ctrl+D is pressed
    while True:
        try:
            # user_choice will store the function which must be called
            # next. This will be done over and over again until a
            # KeyboardInterrupt (Ctrl+C) or EOFError (Ctrl+D)
            # is received
            user_choice = get_user_input()
            user_choice(options)
        except (KeyboardInterrupt, EOFError):
            print('\nGoodby ...')
            break
    # ------------------------------------------------------------ show_menu()


def test():
    """Function to run different calls to analyze."""
    options['interactive'] = False
    for city_dict in city_data:
        print('-' * 80)
        print('Analyzing data for city "{}" ..'.format(city_dict['name']))
        options['city_of_interest'] = city_data[city_data.index(city_dict)]
        analyze(options)
        for month in options['allowed_months']:
            print('-' * 80)
            print('Analyzing again using Filter "Month" for "{}" ..'.format(
                calendar.month_name[month]))
            options['filter_type'] = 'Month'
            options['month_of_interest'] = month
            analyze(options)
            for day in options['allowed_days']:
                print('-' * 80)
                print(
                    'Analyzing again using Filter "Both" for "{}" and "{}" ..'.
                    format(calendar.month_name[month], calendar.day_name[day]))
                options['filter_type'] = 'Both'
                options['day_of_interest'] = day
                analyze(options)
        for day in options['allowed_days']:
            print('-' * 80)
            print('Analyzing again using Filter "Day" for "{}" ..'.format(
                calendar.day_name[day]))
            options['filter_type'] = 'Day'
            options['day_of_interest'] = day
            analyze(options)
    # ----------------------------------------------------------------- test()


def parse_arguments():
    """Parses the given command line arguments and returns a function that
    will be executed next.
    """

    def find_city_dict(city_name):
        """Helper function to find the dict containing the given city_name in
        city_data."""
        for city_dict in city_data:
            if city_dict['name'] == city_name:
                return city_data.index(city_dict)

    arg_parser = ap.ArgumentParser(
        prog='bikeshare-analyzer',
        description=
        'Analyzes bikeshare data of a given city and prints various stats.',
        epilog='Author: Jörg (lovok@postoe.de)')

    # add subparser:
    # Two commands should be allowed: test and analyze
    sub_arg_parser = arg_parser.add_subparsers(
        title='commands',
        description='valid subcommands',
        help='command help',
        dest='command')
    test_command = sub_arg_parser.add_parser('test')
    analyze_command = sub_arg_parser.add_parser(
        'analyze', formatter_class=ap.ArgumentDefaultsHelpFormatter)

    # only the analyze command needs additional arguments
    analyze_command.add_argument(
        '--city',
        help='The name of the city to analyze data from.',
        choices=[city_dict['name'] for city_dict in city_data],
        default=city_data[0]['name'])
    analyze_command.add_argument(
        '--filter',
        help='The filter to use.',
        choices=[filter for filter in options['allowed_filters']])
    analyze_command.add_argument(
        '--month',
        help='If filtered by month, the month to use. ',
        choices=[
            calendar.month_name[month] for month in options['allowed_months']
        ],
        default='January')
    analyze_command.add_argument(
        '--weekday',
        help='If filtered by weekday, the weekday to use.',
        choices=[calendar.day_name[day] for day in options['allowed_days']],
        default='Monday')
    args = arg_parser.parse_args()

    if args.command == 'test':
        return test
    else:
        # change options according to the args given
        # city
        if (args.city and options['city_of_interest']['name'] != args.city):
            options['city_of_interest'] = city_data[find_city_dict(args.city)]

        # filter
        if (args.filter and options['filter_type'] != args.filter):
            options['filter_type'] = args.filter

        # month
        if (options['filter_type'] == "Both"
                or options['filter_type'] == "Month"):
            if (args.month
                    and calendar.month_name[options['month_of_interest']] !=
                    args.month):
                # use dictionary comprehension to find the index of month name
                options['month_of_interest'] = [
                    k for k, v in enumerate(calendar.month_name)
                    if v == args.month
                ][0]

        # day
        if (options['filter_type'] == "Both"
                or options['filter_type'] == "Day"):
            if (args.weekday and calendar.day_name[options['day_of_interest']]
                    != args.weekday):
                # equal to above
                options['day_of_interest'] = [
                    k for k, v in enumerate(calendar.day_name)
                    if v == args.weekday
                ][0]
        return analyze
    # ------------------------------------------------------ parse_arguments()


# Start main -----------------------------------------------------------------
if __name__ == "__main__":
    """Instead of using only an interactive part I decided to implement both:
        - If the user hands over command line arguments I assume that he wants
          to calculate the statistics in silent mode without user input.
        - Otherwise I'll print a menu on screen. This menu will only show
          allowed options which can be selected by number.
    """

    # set up default data structures -----------------------------------------
    # city_data is a tuple of dicts. This is done to be able to display the
    # cities by number in a menu and to access the dictionaries by name.
    city_data = (
        {
            'name': 'Chicago',
            'file': 'chicago.csv'
        },
        {
            'name': 'New York City',
            'file': 'new_york_city.csv'
        },
        {
            'name': 'Washington',
            'file': 'washington.csv'
        },
    )
    # the city to use and the filter are stored in a dictionary which is
    # passed around the functions
    options = {
        'city_of_interest': city_data[0],
        'filter_type': None,
        'month_of_interest': 1,
        'day_of_interest': 0,
        'allowed_filters': ('None', 'Month', 'Day', 'Both'),
        'allowed_months': list(range(1, 7)),
        'allowed_days': list(range(0, 7)),
        'interactive': True,
    }

    if len(sys.argv) == 1:
        show_menu()
    else:
        options['interactive'] = False
        action = parse_arguments()
        action(options)
