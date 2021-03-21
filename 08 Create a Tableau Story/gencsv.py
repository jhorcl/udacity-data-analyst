#!/usr/bin/env python
"""Generate Tableau data from pisa 2012 database."""

import pandas as pd


def return_time_category(value):
    """Return category of time value."""
    category = {
        1: 'Once or twice a month',
        2: 'Once or twice a week',
        3: 'Almost every day',
        4: 'Every day',
        0: 'Never or hardly ever'
    }
    if not pd.isnull(value):
        return category.get(value)
    else:
        return value


# COUNTRIES ATTENDED TO THE DIGITAL ASSESSMENT
countries = [
    'Australia', 'Austria', 'Belgium', 'Switzerland', 'Chile', 'Costa Rica',
    'Czech Republic', 'Germany', 'Denmark', 'Spain', 'Estonia', 'Finland',
    'Greece', 'Hong Kong-China', 'Croatia', 'Hungary', 'Ireland', 'Iceland',
    'Israel', 'Italy', 'Jordan', 'Japan', 'Korea', 'Liechtenstein', 'Latvia',
    'Macao-China', 'Mexico', 'Netherlands', 'Norway', 'New Zealand', 'Poland',
    'Portugal', 'China-Shanghai', 'Perm(Russian Federation)',
    'Russian Federation', 'Singapore', 'Serbia', 'Slovak Republic', 'Slovenia',
    'Sweden', 'Chinese Taipei', 'Turkey', 'Uruguay'
]

# COLUMNS TO IMPORT
cols = [
    'CNT', 'OECD', 'IC01Q01', 'IC01Q02', 'IC01Q03', 'IC01Q04',
    'IC01Q05', 'IC01Q06', 'IC01Q07', 'IC01Q08', 'IC01Q09', 'IC01Q10',
    'IC01Q11', 'IC02Q01', 'IC02Q02', 'IC02Q03', 'IC02Q04', 'IC02Q05',
    'IC02Q06', 'IC02Q07', 'IC10Q01', 'IC10Q02', 'IC10Q03', 'IC10Q04',
    'IC10Q05', 'IC10Q06', 'IC10Q07', 'IC10Q08', 'IC10Q09', 'PV1MATH',
    'PV2MATH', 'PV3MATH', 'PV4MATH', 'PV5MATH', 'PV1READ', 'PV2READ',
    'PV3READ', 'PV4READ', 'PV5READ', 'PV1SCIE', 'PV2SCIE', 'PV3SCIE',
    'PV4SCIE', 'PV5SCIE'
]

# COUNTRY NAMES TO FIX/REPLACE
country_values = {
    'Korea': 'South Korea',
    'Perm(Russian Federation)': 'Russian Federation',
    'Chinese Taipei': 'Taiwan',
    'China-Shanghai': 'China'
}

# ICT CODINGS
usage_values = {
    'No': '0',
    'Yes, but I don’t use it': '1',
    'Yes, and I use it': '2'
}

# TIME CODINGS
time_values = {
    'Never or hardly ever': '0',
    'Once or twice a month': '1',
    'Once or twice a week': '2',
    'Almost every day': '3',
    'Every day': '4'
}

# READ FILE
df = pd.read_csv(
    'pisa2012.csv', encoding='cp1252', usecols=cols, dtype=object,
    memory_map=True)

# ONLY HOLD ROWS OF ABOVE COUNTRIES
df = df.loc[df.CNT.isin(countries), ]

# REPLACE COUNTRY NAMES
df['CNT'] = df.loc[:, 'CNT'].replace(to_replace=country_values)

# REPLACE USAGE VALUES
df.loc[:, 'IC01Q01':'IC02Q07'] = df.loc[:, 'IC01Q01':'IC02Q07'].replace(
    to_replace=usage_values)

# REPLACE TIME INFORMATION
df.loc[:, 'IC10Q01':'IC10Q09'] = df.loc[:, 'IC10Q01':'IC10Q09'].replace(
    to_replace=time_values)

# CONVERT COLUMNS TO FLOAT
df[cols[2:]] = df[cols[2:]].apply(pd.to_numeric)

# CREATE COLUMN FOR 'DOES THE STUDENT HAS ACCESS TO ICT AT HOME?'
df['ict_avail_home'] = df.loc[:, 'IC01Q01':'IC01Q11'].max(axis=1).replace(
    to_replace=2.0, value=1.0)

# CREATE COLUMN FOR 'DOES THE STUDENT HAS ACCESS TO ICT AT SCHOOL?'
df['ict_avail_school'] = df.loc[:, 'IC02Q01':'IC02Q07'].max(axis=1).replace(
    to_replace=2.0, value=1.0)

# CREATE COLUMN FOR 'DOES THE STUDENT USE THE ICT HE HAS ACCESS TO AT HOME?'
df['ict_used_home'] = df.loc[:, 'IC01Q01':'IC01Q11'].max(axis=1).replace(
    to_replace=1.0, value=0.0).replace(to_replace=2.0, value=1.0)

# CREATE COLUMN FOR 'DOES THE STUDENT USE THE ICT HE HAS ACCESS TO AT SCHOOL?'
df['ict_used_school'] = df.loc[:, 'IC02Q01':'IC02Q07'].max(axis=1).replace(
    to_replace=1.0, value=0.0).replace(to_replace=2.0, value=1.0)

# CREATE COLUMN FOR 'HOW LONG DOES THE STUDENT USE ICT AT SCHOOL ON AVERAGE?'
df['ict_usage_time_school'] = df.loc[:, 'IC10Q01':'IC10Q09'].mean(
    axis=1).round().apply(return_time_category)

# CREATE COLUMN FOR AVERAGE MATH SCORE
df['math_score'] = df.loc[:, 'PV1MATH':'PV5MATH'].mean(axis=1)

# CREATE COLUMN FOR AVERAGE READING SCORE
df['read_score'] = df.loc[:, 'PV1READ':'PV5READ'].mean(axis=1)

# CREATE COLUMN FOR AVERAGE SCIENCE SCORE
df['scie_score'] = df.loc[:, 'PV1SCIE':'PV5SCIE'].mean(axis=1)

# DROP COLUMNS
df.drop(columns=cols[2:], inplace=True)

# RENAME COLUMNS
df.rename(index=str, columns={'CNT': 'Country'}, inplace=True)
df.rename(str.lower, axis='columns', inplace=True)

# WRITE OUT CSV
df.to_csv('tableau.csv', index=False, encoding='utf-8')
