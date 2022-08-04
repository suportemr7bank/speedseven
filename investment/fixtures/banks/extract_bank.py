"Convert bank cls data to json"

import csv
import json
import os

def make_json(csv_file_path, json_file_path):
    """ convert do json """

    data = []

    with open(csv_file_path, encoding='utf-8') as csvf:
        csv_reader = csv.DictReader(csvf)

        for rows in csv_reader:
            code = rows['code'] if rows['code'] else None
            data.append(
                {
                    'model': "investment.bank",
                    'pk': int(rows['pk']),
                    'fields': {
                        "ispb": rows['ispb'],
                        "code": code,
                        "name": rows['name'].strip()

                    }
                }
            )

    with open(json_file_path, 'w', encoding='utf-8') as jsonf:
        json.dump(data, jsonf, indent=4, ensure_ascii=False)

path = f'{os.getcwd()}/investment/fixtures/banks/'
make_json(path +'banks.csv', path + 'banks.json')
