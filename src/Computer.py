import simpy
import random
import matplotlib.pyplot as plt
import numpy as np

# Parametros de simulacion
RANDOM_SEED = 42
SIMULATION_TIME = 5000
PROCESS_CREATION_INTERVAL = 10
RAM_CAPACITY = 100
INSTRUCTIONS_PER_CYCLE = 3
CPU_SPEED = 1
CPU_QUANTITY = 1 
PROCESS_QUANTITY = 25

random.seed(RANDOM_SEED) # Se utiliza la seed para asegurarme que todo salga igual en la ejecucion

process_durations = []  # Almacenará la duración de cada proceso

class OperatingSystem:
    def __init__(self, env):
        self.RAM = simpy.Container(env, init=RAM_CAPACITY, capacity=RAM_CAPACITY)
        self.CPU = simpy.Resource(env, capacity=CPU_QUANTITY)
        self.env = env

    def process(self, name, required_memory, total_instructions):
        start_time = self.env.now  # Tiempo de inicio
        yield self.RAM.get(required_memory)
        print(f'{self.env.now}: El proceso {name} ha obtenido {required_memory} de RAM')

        while total_instructions > 0:
            with self.CPU.request() as req:
                yield req
                print(f'{self.env.now}: El proceso {name} ha comenzado su ejecución en CPU')
                yield self.env.timeout(CPU_SPEED)
                total_instructions -= min(INSTRUCTIONS_PER_CYCLE, total_instructions)
                print(f'{self.env.now}: El proceso {name} ha completado instrucciones, {total_instructions} restantes')

            if total_instructions > 0:  # Aqui decidira si ir estar en waiting o ready
                event = random.randint(1, 2)
                if event == 1:
                    print(f'{self.env.now}: El proceso {name} ha pasado a waiting')
                    yield self.env.timeout(1)  # Simulate waiting time for I/O
                print(f'{self.env.now}: El proceso {name} está listo para continuar')
        
        print(f'{self.env.now}: El proceso {name} ha terminado')
        end_time = self.env.now  # Tiempo de finalización
        process_durations.append(end_time - start_time)  # Añadir la duración del proceso
        self.RAM.put(required_memory)

def process_generator(env, os):
    for i in range(PROCESS_QUANTITY):
        required_memory = random.randint(1, 10)
        total_instructions = random.randint(1, 10)
        env.process(os.process(f'Proceso {i}', required_memory, total_instructions))
        yield env.timeout(random.expovariate(1.0 / PROCESS_CREATION_INTERVAL))

# Inicia la simulacion
env = simpy.Environment()
os = OperatingSystem(env)
env.process(process_generator(env, os))
env.run(until=SIMULATION_TIME)

# Cálculo de promedio y desviación estándar
average_time = np.mean(process_durations)
std_dev = np.std(process_durations)

# Gráfica
plt.figure(figsize=(10, 6))
plt.bar(range(PROCESS_QUANTITY), process_durations, color='skyblue', label='Duración por proceso')
plt.axhline(y=average_time, color='r', linestyle='-', label=f'Tiempo Promedio = {average_time:.2f}')
plt.xlabel('Número de Proceso')
plt.ylabel('Tiempo en Computadora')
plt.title('Tiempo de Procesos en la Computadora')
plt.legend()
plt.show()

print(f"Tiempo Promedio: {average_time:.2f}")
print(f"Desviación Estándar: {std_dev:.2f}")
