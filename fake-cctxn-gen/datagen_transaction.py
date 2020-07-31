from __future__ import division
import random
import pandas as pd
from pandas import *
import json
import numpy as np
import sys
import datetime
import time
from datetime import timedelta
from datetime import date
import math
from random import sample
from random import randint
from faker import Faker
from faker import Factory
from decimal import Decimal
from utils import profile_weights

def get_user_input():
    # convert date to datetime object
    def convert_date(d):
        for char in ['/', '-', '_', ' ']:
            if char in d:
                d = d.split(char)
                try:
                    return date(int(d[2]), int(d[0]), int(d[1]))
                except:
                    error_msg(3)
        error_msg(3)

    # error handling for CL inputs
    def error_msg(n):
        if n == 1:
            print('Could not open customers file\n')
        elif n == 2:
            print ('Could not open main config json file\n')
        else:
            print('Invalid date (MM-DD-YYYY)')
        output = 'ENTER:\n(1) Customers csv file\n'
        output += '(2) profile json file\n'
        output += '(3) Base Home Directory\n'
        output += '(4) Start date (MM-DD-YYYY)\n'
        output += '(5) End date (MM-DD-YYYY)\n'
        output += '(6) Base File Name\n'
        print(output)
        sys.exit(0)

    try:
        customers = open(sys.argv[1], 'r').readlines()
        #manojs
        # Includes customer information in the Transactions
        cstmr = []
        for row_parsed in customers:
             cc_num=row_parsed.split('|')[1]
             acct_num=row_parsed.split('|')[14]
             profile=row_parsed.split('|')[15]
             profile=profile[:-1]
             c_state=row_parsed.split('|')[7]
             c_lat=row_parsed.split('|')[9]
             c_long=row_parsed.split('|')[10]
             merged_row = cc_num+'|'+acct_num+'|'+profile+'|'+c_state+'|'+c_lat+'|'+c_long
             cstmr.append(merged_row)
    except:
        error_msg(1)
    try:
        # Only generates and plays with file names
        m = str(sys.argv[2])
        pro_name = m.split('profiles')[-1]
        pro_name = pro_name[1:]
        parse_index = m.index('profiles') + 9
        m_fraud = m[:parse_index] +'fraud_' + m[parse_index:]

        # Open all profile files
        pro = open(m, 'r').read()
        pro_fraud = open(m_fraud, 'r').read()
        pro_name_fraud = 'fraud_' + pro_name

    except:
        error_msg(2)
    try:
        base_home = str(sys.argv[3])
    except:
        error_msg(3)
    try:
        startd = convert_date(sys.argv[4])
    except:
        error_msg(4)
    try:
        endd = convert_date(sys.argv[5])
    except:
        error_msg(5)
    try:
        base_file_name = str(sys.argv[6])
    except:
        error_msg(6)

    return cstmr, pro, pro_fraud, pro_name, pro_name_fraud, base_home, startd, endd, m, base_file_name

def create_header(line):
    headers = line.split('|')
    headers[-1] = headers[-1].replace('\n','')
    headers.extend(['trans_num', 'trans_date', 'trans_time','unix_time', 'category', 'amt', 'is_fraud', 'merchant', 'merch_lat', 'merch_long'])
    print('trans_num' + '|' + ''.join([h + '|' for h in headers])[:-1])
    return headers


class Customer:
    def __init__(self, customer, profile):
        self.customer = customer
        self.attrs = self.clean_line(self.customer)
        self.fraud_dates = []

    def print_trans(self, trans, is_fraud, fraud_dates):

        is_traveling = trans[1]
        travel_max = trans[2]

        for t in trans[0]:

            ## Get transaction location details to generate appropriate merchant record
            cust_state = cust.attrs['state']
            groups = t.split('|')
            trans_cat = groups[4]

            ## COllect transaction id to appen as primary key for Kudu - manojs
            tid = groups[0]

            merch_filtered = merch[merch['category'] == trans_cat]
            #random_row = merch_filtered.ix[random.sample(merch_filtered.index, 1)]
            #random_row = merch_filtered.loc[merch_filtered.index[random.sample(merch_filtered.index, 1)]]
            random_row = merch_filtered.loc[random.sample(list(merch_filtered.index),1)]
            ##sw added list
            chosen_merchant = random_row.iloc[0]['merchant_name']

            cust_lat = cust.attrs['lat']
            cust_long = cust.attrs['long']

            faker = Factory.create()

            if is_traveling:
                # hacky math.. assuming ~70 miles per 1 decimal degree of lat/long
                # sorry for being American, you're on your own for kilometers.
                rad = (float(travel_max) / 100) * 1.43

                #geo_coordinate() uses uniform distribution with lower = (center-rad), upper = (center+rad)
                #merch_lat = fake.geo_coordinate(center=float(cust_lat),radius=rad)
                #merch_long = fake.geo_coordinate(center=float(cust_long),radius=rad)
                merch_lat = faker.coordinate(center=float(cust_lat),radius=rad)
                merch_long = faker.coordinate(center=float(cust_long),radius=rad)
            else:
                # otherwise not traveling, so use 1 decimial degree (~70mile) radius around home address
                rad = 1
                merch_lat = faker.coordinate(center=float(cust_lat),radius=rad)
                merch_long = faker.coordinate(center=float(cust_long),radius=rad)

            csv_lines = ''
            if is_fraud == 0 and groups[1] not in fraud_dates:
            # if cust.attrs['profile'] == "male_30_40_smaller_cities.json":
                csv_lines += (self.customer.replace('\n','') + '|' + t + '|' + str(chosen_merchant) + '|' + str(merch_lat) + '|' + str(merch_long) + '\n')

            if is_fraud ==1:
                csv_lines += (self.customer.replace('\n','') + '|' + t + '|' + str(chosen_merchant) + '|' + str(merch_lat) + '|' + str(merch_long) + '\n')

            #else:
                # pass
            return csv_lines


    def clean_line(self, line):
        # separate into a list of attrs
        cols = [c.replace('\n','') for c in line.split('|')]
        # create a dict of name:value for each column
        attrs = {}
        for i in range(len(cols)):
            attrs[headers[i].replace('\n','')] = cols[i].replace('\n','')
        return attrs

if __name__ == '__main__':
    # read user input into Inputs object
    # to prepare the user inputs
    # curr_profile is female_30_40_smaller_cities.json , for fraud as well as non fraud
    # profile_name is ./profiles/fraud_female_30_40_bigger_cities.json for fraud.
    cstmr, pro, pro_fraud, curr_profile, curr_fraud_profile, base_home, start, end, profile_name, base_file_name = get_user_input()
    #if curr_profile == "male_30_40_smaller_cities.json":
    #   inputCat = "travel"
    #elif curr_profile == "female_30_40_smaller_cities.json":
    #    inputCat = "pharmacy"
    #else:
    #    inputCat = "misc_net"

    # takes the customers headers and appends
    # transaction headers and returns/prints
    #if profile_name[11:][:6] == 'fraud_':
    # read merchant.csv used for transaction record
    #    merch = pd.read_csv('./data/merchants_fraud.csv' , sep='|')
    #else:
    #    merch = pd.read_csv('./data/merchants.csv', sep='|')

    headers = create_header(cstmr[0])
    # generate Faker object to calc merchant transaction locations
    fake = Faker()

    # merchants_reference_path
    merchants_reference_path = base_home + "/data/reference_data/merchants.csv"

    # for each customer, if the customer fits this profile
    # generate appropriate number of transactions
    i = 0
    output_lines = (''.join([h + '|' for h in headers])[:-1] + '\n')
    for line in cstmr[1:]:

            i += 1

            profile = profile_weights.Profile(pro, start, end)
            cust = Customer(line, profile)
            #print(cust.attrs['profile'])
            if cust.attrs['profile'] == curr_profile:
                merch = pd.read_csv(merchants_reference_path, sep='|')
                is_fraud= 0

                fraud_flag = randint(0,100) # set fraud flag here, as we either gen real or fraud, not both for
                                        # the same day
                fraud_dates = []


                # decide if we generate fraud or not
                if fraud_flag < 99: #11->25
                    fraud_interval = randint(1,1) #7->1
                    inter_val = (end-start).days-7
                    # rand_interval is the random no of days to be added to start date
                    rand_interval = randint(1, inter_val)
                    #random start date is selected
                    newstart = start + datetime.timedelta(days=rand_interval)
                    # based on the fraud interval , random enddate is selected
                    newend = newstart + datetime.timedelta(days=fraud_interval)
                    # we assume that the fraud window can be between 1 to 7 days #7->1
                    profile = profile_weights.Profile(pro_fraud, newstart, newend)
                    cust = Customer(line, profile)
                    merch = pd.read_csv(merchants_reference_path, sep='|')
                    is_fraud = 1
                    temp_tx_data = profile.sample_from(is_fraud)
                    fraud_dates = temp_tx_data[3]

                    if cust is not None:
                        output_lines += str(cust.print_trans(temp_tx_data,is_fraud, fraud_dates))

                    #parse_index = m.index('profiles/') + 9
                    #m = m[:parse_index] +'fraud_' + m[parse_index:]

                # we're done with fraud (or didn't do it) but still need regular transactions
                # we pass through our previously selected fraud dates (if any) to filter them
                # out of regular transactions
                profile = profile_weights.Profile(pro, start, end)
                merch = pd.read_csv(merchants_reference_path, sep='|')
                is_fraud = 0
                temp_tx_data = profile.sample_from(is_fraud)

                if cust is not None:
                    output_lines += str(cust.print_trans(temp_tx_data, is_fraud, fraud_dates))

            # Print every 10 objects to a new file
            if i % 10 == 0 and len(output_lines.splitlines()) > 1:
                new_filename = base_file_name + "_" + str(int(time.time())) + ".csv"
                with open(new_filename, "a+") as text_file:
                    print("{}".format(output_lines), file=text_file)
                output_lines = (''.join([h + '|' for h in headers])[:-1] + '\n')

