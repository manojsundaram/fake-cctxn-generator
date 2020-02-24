#!/bin/bash

set -x
rm -rf /data/
mkdir -p /data/reference_data /data/transactions
cp ../fake-cctxn-gen/demographic_data/* /data/reference_data
python3 ../fake-cctxn-gen/pos_merchant_generator.py >> /data/reference_data/merchants.csv
python3 ../fake-cctxn-gen/datagen_customer.py 10000 4444 ../fake-cctxn-gen/profiles/main_config.json >> /data/reference_data/customers.csv

# Enter your allowed profiles
for i in adults_2550_female_rural.json adults_2550_female_urban.json adults_2550_male_rural.json adults_2550_male_urban.json adults_50up_female_rural.json adults_50up_female_urban.json adults_50up_male_rural.json adults_50up_male_urban.json young_adults_female_rural.json young_adults_female_urban.json young_adults_male_rural.json young_adults_male_urban.json
do
	fname=`echo $i | awk -F "." '{print $1}'`
	python3 ../fake-cctxn-gen/datagen_transaction.py /data/reference_data/customers.csv ../fake-cctxn-gen/profiles/$i 12-30-2018 12-30-2019 >> /data/transactions/$fname.csv &
done
mkdir -p /data/reference_data_in/
sed 1d /data/reference_data/age_gender_demographics.csv > /data/reference_data_in/age_gender_demographics.csv
sed 1d /data/reference_data/customers.csv  > /data/reference_data_in/customers.csv
sed 1d /data/reference_data/locations_partitions.csv > /data/reference_data_in/locations_partitions.csv
sed 1d /data/reference_data/merchants.csv > /data/reference_data_in/merchants.csv

SCRIPT=$(readlink -f "$0")
SCRIPTPATH=$(dirname "$SCRIPT")


$SCRIPTPATH/txn.sh

chmod -R 777 /data
set +x
