#!/bin/bash

set -x

usage()
{
cat << EOF
FAIL:
usage: $0 options

Examples:
$ ./01-generate-customerdata.sh -d /tmp/fake-cctxn-generator -c 1000000 -b 07-30-2017 -e 07-30-2020

OPTIONS:
   -h     Help
   -d     Generator Home Directory, where the git cloned folder
   -c     Customer Count
   -b     Transaction Begin Date
   -e     Transaction End Date

EOF
}

GENERATOR_HOME=
CUSTOMER_NUM=
TXN_BEGIN=
TXN_END=
NOW="$(date +'%m-%d-%Y')"

while getopts "hd:c:b:e:" OPTION
do
     case $OPTION in
         h)
             usage
             exit 1
             ;;
         d)
             GENERATOR_HOME=$OPTARG
             ;;
         c)
             CUSTOMER_NUM=$OPTARG
             ;;
         b)
             TXN_BEGIN=$OPTARG
             ;;
         e)
             TXN_END=$OPTARG
             ;;
         ?)
             usage
             exit 1
             ;;
     esac
done

if [[ -z $GENERATOR_HOME ]] || [[ -z $CUSTOMER_NUM ]] || [[ -z $TXN_BEGIN ]] || [[ -z $TXN_END ]]
then
  usage
  exit 1
fi

pip3 install -r $GENERATOR_HOME/init/requirements.txt
rm -rf $GENERATOR_HOME/data/
mkdir -p $GENERATOR_HOME/data/reference_data $GENERATOR_HOME/data/transactions
cp $GENERATOR_HOME/fake-cctxn-gen/demographic_data/* $GENERATOR_HOME/data/reference_data
python3 $GENERATOR_HOME/fake-cctxn-gen/pos_merchant_generator.py >> $GENERATOR_HOME/data/reference_data/merchants.csv
python3 $GENERATOR_HOME/fake-cctxn-gen/datagen_customer.py $CUSTOMER_NUM 4444 $GENERATOR_HOME/fake-cctxn-gen/profiles/main_config.json >> $GENERATOR_HOME/data/reference_data/customers.csv

# Enter your allowed profiles
for i in adults_2550_female_rural.json adults_2550_female_urban.json adults_2550_male_rural.json adults_2550_male_urban.json adults_50up_female_rural.json adults_50up_female_urban.json adults_50up_male_rural.json adults_50up_male_urban.json young_adults_female_rural.json young_adults_female_urban.json young_adults_male_rural.json young_adults_male_urban.json
do
	fname=`echo $i | awk -F "." '{print $1}'`
	python3 $GENERATOR_HOME/fake-cctxn-gen/datagen_transaction.py $GENERATOR_HOME/data/reference_data/customers.csv $GENERATOR_HOME/fake-cctxn-gen/profiles/$i $GENERATOR_HOME $TXN_BEGIN $TXN_END $GENERATOR_HOME/data/transactions/$fname &
done
mkdir -p $GENERATOR_HOME/data/reference_data_in/
sed 1d $GENERATOR_HOME/data/reference_data/age_gender_demographics.csv > $GENERATOR_HOME/data/reference_data_in/age_gender_demographics.csv
sed 1d $GENERATOR_HOME/data/reference_data/customers.csv  > $GENERATOR_HOME/data/reference_data_in/customers.csv
sed 1d $GENERATOR_HOME/data/reference_data/locations_partitions.csv > $GENERATOR_HOME/data/reference_data_in/locations_partitions.csv
sed 1d $GENERATOR_HOME/data/reference_data/merchants.csv > $GENERATOR_HOME/data/reference_data_in/merchants.csv

#SCRIPT=$(readlink -f "$0")
#SCRIPTPATH=$(dirname "$SCRIPT")

#$SCRIPTPATH/txn.sh > /var/log/txn.log 2>&1

chmod -R 777 $GENERATOR_HOME/data
set +x
