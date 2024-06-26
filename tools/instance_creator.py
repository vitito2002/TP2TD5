import csv
import random
import json
import copy

def convertir_json(filename,costo_1,costo_2,estacion_1,estacion_2,capacity,max_rs):
    instance = {}
    instance['services'] = {}
    instance['stations'] = [estacion_2,estacion_1]
    instance['cost_per_unit'] = {estacion_2 : costo_2, estacion_1 : costo_1}

    with open(filename + '.csv', 'r') as csvfile:
        # Create a CSV reader object
        csvreader = csv.reader(csvfile)
        next(csvreader)
        
        # Loop through each row in the CSV file
        for row in csvreader:
            # Each row is a list of values, you can access them by index
            service_id = row[0]
            instance['services'][service_id] = {}
            dep = {'time': int(row[1]), 'station':str(row[2]), 'type':str(row[3])}
            arr = {'time': int(row[4]), 'station':str(row[5]), 'type':str(row[6])}
            instance['services'][service_id]['stops'] = copy.deepcopy([dep,arr])
            instance['services'][service_id]['demand'] = [int(row[7])]


    instance['rs_info'] = {'capacity': capacity, 'max_rs': max_rs}

    with open(filename + '.json', 'w') as json_file:
        json.dump(instance, json_file)


def generar_csv(filename, cantidad_servicios, horario_min, horario_max, estacion_1, estacion_2, demanda_min, demanda_max):
    horarios_unicos = set()

    while len(horarios_unicos) < 2 * cantidad_servicios: 
        horario = random.randint(horario_min, horario_max)
        horarios_unicos.add(horario)

    horarios = sorted(list(horarios_unicos))

    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["service id", "hora", "origen", "tipo", "hora", "destino", "tipo", "demanda (pax)"])

        for i in range(1, cantidad_servicios + 1):
            hora_origen = horarios.pop(0)
            hora_destino = horarios.pop(0)

            origen = random.choice([estacion_1, estacion_2])
            destino = estacion_2 if origen == estacion_1 else estacion_1

            demanda = random.randint(demanda_min, demanda_max)

            writer.writerow([i, hora_origen, origen, "D", hora_destino, destino, "A", demanda])

filename = "exp_5.csv"
file_csv = "exp_5"

cantidad_servicios = 5 # viajes

horario_min = 200
horario_max = 300

estacion_1 = "Narnia"
estacion_2 = "Springfield"

demanda_min = 10
demanda_max = 700

costo_1 = 1
costo_2 = 1

capacity = 100
max_rs = 25

if capacity * max_rs < demanda_max: ## CHEQUEAR BIEN ESTO NO SE COMO ES
    raise ValueError("El valor de max_rs es demasiado pequeño para manejar la demanda total.")

#generar_csv(filename, cantidad_servicios, horario_min, horario_max, estacion_1, estacion_2, demanda_min, demanda_max)
convertir_json(file_csv,costo_1,costo_2,estacion_1,estacion_2,capacity,max_rs)