import simpy
import random
import matplotlib.pyplot as plt
import numpy as np  

# Parámetros de simulación ajustados
RANDOM_SEED = 42
SIMULATION_TIME = 100000
PROCESS_CREATION_INTERVAL = 1 
RAM_CAPACITY = 100 
INSTRUCTIONS_PER_CYCLE = 3
CPU_SPEED = 1
CPU_QUANTITY = 2
PROCESS_QUANTITY = 200

random.seed(RANDOM_SEED)

process_durations = []

class OperatingSystem:
    def __init__(self, env):
        self.env = env
        self.RAM = simpy.Container(env, init=RAM_CAPACITY, capacity=RAM_CAPACITY)
        self.CPU = simpy.Resource(env, capacity=CPU_QUANTITY)

    def allocate_memory(self, name, required_memory):
        yield self.RAM.get(required_memory)
        print(f'{self.env.now}: El proceso {name} ha obtenido {required_memory} de RAM')

    def execute_process(self, name, total_instructions):
        while total_instructions > 0:
            with self.CPU.request() as req:
                yield req
                executed_instructions = min(INSTRUCTIONS_PER_CYCLE, total_instructions)
                yield self.env.timeout(CPU_SPEED)  # Simula el tiempo de procesamiento
                total_instructions -= executed_instructions
                print(f'{self.env.now}: El proceso {name} ha completado instrucciones, {total_instructions} restantes')

    def release_memory(self, name, required_memory):
        yield self.RAM.put(required_memory)
        print(f'{self.env.now}: El proceso {name} ha liberado {required_memory} de RAM')

    def process(self, name, required_memory, total_instructions):
        start_time = self.env.now
        yield self.env.process(self.allocate_memory(name, required_memory))
        yield self.env.process(self.execute_process(name, total_instructions))
        process_durations.append(self.env.now - start_time)
        yield self.env.process(self.release_memory(name, required_memory))
        print(f'{self.env.now}: El proceso {name} ha terminado')

def gen_process(env, os):
    for i in range(PROCESS_QUANTITY):
        required_memory = random.randint(1, 10)
        total_instructions = random.randint(1, 10)
        process_name = f'Proceso {i}'
        env.process(os.process(process_name, required_memory, total_instructions))
        yield env.timeout(random.expovariate(1.0 / PROCESS_CREATION_INTERVAL))

env = simpy.Environment()
os = OperatingSystem(env)
env.process(gen_process(env, os))
env.run(until=SIMULATION_TIME)

average_time = np.mean(process_durations)
std_dev = np.std(process_durations)

plt.figure(figsize=(10, 6))
plt.bar(range(len(process_durations)), process_durations, color='skyblue', label='Duración por proceso')
plt.axhline(y=average_time, color='r', linestyle='-', label=f'Tiempo Promedio = {average_time:.2f}')
plt.xlabel('Número de Proceso')
plt.ylabel('Tiempo en Computadora')
plt.title('Tiempo de Procesos en la Computadora')
plt.legend()
plt.show()

print(f"Tiempo Promedio: {average_time:.2f}")
print(f"Desviación Estándar: {std_dev:.2f}")
