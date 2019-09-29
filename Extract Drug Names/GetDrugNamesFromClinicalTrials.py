import psycopg2
import csv

try:
    connection = psycopg2.connect(user="thisisvikaas",
                                  password="nnnM4Mdx5PFYvux",
                                  host="aact-db.ctti-clinicaltrials.org",
                                  port="5432",
                                  database="aact")
    cursor = connection.cursor()
    postgreSQL_select_Query = "select name from interventions where intervention_type = 'Drug'"

    mobile_records = []
    cursor.execute(postgreSQL_select_Query)
    mobile_records = cursor.fetchall()

except (Exception, psycopg2.Error) as error:
    print("Error while fetching data from PostgreSQL", error)

finally:
    # closing database connection.
    if (connection):
        cursor.close()
        connection.close()

with open('drugsfromtrials.csv','w', encoding="utf-8", newline="\n") as myFile:
    wr = csv.writer(myFile, lineterminator="\n")
    for val in mobile_records:
        wr.writerow([val])

