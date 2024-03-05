import simpy
import random
import matplotlib.pyplot as plt
import numpy as np

# Parámetros de simulación
RANDOM_SEED = 42
SIMULATION_TIME = 500
PROCESS_CREATION_INTERVAL = 10
RAM_CAPACITY = 100
INSTRUCTIONS_PER_CYCLE = 3
CPU_SPEED = 1
CPU_QUANTITY = 1 
PROCESS_QUANTITY = 25

random.seed(RANDOM_SEED) # Se utiliza la seed para asegurarme que todo salga igual en la ejecución

process_durations = []  # Almacenará la duración de cada proceso

class OperatingSystem:
    def __init__(self, env):
        self.env = env
        self.RAM = simpy.Container(env, init=RAM_CAPACITY, capacity=RAM_CAPACITY)
        self.CPU = simpy.Resource(env, capacity=CPU_QUANTITY)

    def allocate_memory(self, name, required_memory):
        """Asigna la memoria requerida para el proceso."""
        yield self.RAM.get(required_memory)
        print(f'{self.env.now}: El proceso {name} ha obtenido {required_memory} de RAM')

    def execute_process(self, name, total_instructions):
        """Ejecuta las instrucciones del proceso en la CPU."""
        while total_instructions > 0:
            with self.CPU.request() as req:
                yield req
                executed_instructions = yield self.env.process(self.perform_cpu_cycle(name, total_instructions))
                total_instructions -= executed_instructions

    def perform_cpu_cycle(self, name, total_instructions):
        """Realiza un ciclo de CPU, ejecutando instrucciones y retornando el número de instrucciones ejecutadas."""
        print(f'{self.env.now}: El proceso {name} ha comenzado su ejecución en CPU')
        yield self.env.timeout(CPU_SPEED)
        executed_instructions = min(INSTRUCTIONS_PER_CYCLE, total_instructions)
        print(f'{self.env.now}: El proceso {name} ha completado instrucciones, {total_instructions - executed_instructions} restantes')
        return executed_instructions

    def check_for_waiting(self, name, total_instructions):
        """Verifica si el proceso necesita esperar debido a operaciones de I/O."""
        if total_instructions > 0:
            event = random.randint(1, 2)
            if event == 1:
                print(f'{self.env.now}: El proceso {name} ha pasado a waiting')
                yield self.env.timeout(1)
            print(f'{self.env.now}: El proceso {name} está listo para continuar')

    def release_memory(self, name, required_memory):
        """Libera la memoria utilizada por el proceso."""
        yield self.RAM.put(required_memory)
        print(f'{self.env.now}: El proceso {name} ha liberado {required_memory} de RAM')

    def process(self, name, required_memory, total_instructions):
        start_time = self.env.now
        yield self.env.process(self.allocate_memory(name, required_memory))
        yield self.env.process(self.execute_process(name, total_instructions))
        # Aquí se debe verificar si hay instrucciones restantes para decidir si se espera o no.
        if total_instructions > 0:
            yield self.env.process(self.check_for_waiting(name, total_instructions))
        process_durations.append(self.env.now - start_time)
        yield self.env.process(self.release_memory(name, required_memory))
        print(f'{self.env.now}: El proceso {name} ha terminado')

def gen_process(env, os):
    """Generador de procesos para la simulación."""
    for i in range(PROCESS_QUANTITY):
        required_memory = random.randint(1, 10)
        total_instructions = random.randint(1, 10)
        process_name = f'Proceso {i}'
        env.process(os.process(process_name, required_memory, total_instructions))
        yield env.timeout(random.expovariate(1.0 / PROCESS_CREATION_INTERVAL))

# Inicia la simulación
env = simpy.Environment()
os = OperatingSystem(env)
env.process(gen_process(env, os))
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
