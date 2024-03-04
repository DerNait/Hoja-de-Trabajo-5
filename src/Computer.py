import simpy
import random

# Parametros de simulacion
RANDOM_SEED = 42
SIMULATION_TIME = 500
PROCESS_CREATION_INTERVAL = 10
RAM_CAPACITY = 100
INSTRUCTIONS_PER_CYCLE = 3
CPU_SPEED = 1 
PROCESS_QUANTITY = 25

random.seed(RANDOM_SEED) #Se utiliza la semilla para asegurarme que todo salga igual en la ejecucion

class OperatingSystem:
    def __init__(self, env):
        self.RAM = simpy.Container(env, init=RAM_CAPACITY, capacity=RAM_CAPACITY)
        self.CPU = simpy.Resource(env, capacity=1)
        self.env = env

    def process(self, name, required_memory, total_instructions):
        yield self.RAM.get(required_memory)
        print(f'{env.now}: El proceso {name} ha obtenido {required_memory} de RAM')

        while total_instructions > 0:
            with self.CPU.request() as req:
                yield req
                print(f'{env.now}: El proceso {name} ha comenzado su ejecución en CPU')
                # Simulate the execution of instructions
                yield env.timeout(CPU_SPEED)
                total_instructions -= min(INSTRUCTIONS_PER_CYCLE, total_instructions)
                print(f'{env.now}: El proceso {name} ha completado instrucciones, {total_instructions} restantes')

            if total_instructions > 0:  # Decide whether to go to waiting or to ready
                event = random.randint(1, 2)
                if event == 1:
                    print(f'{env.now}: El proceso {name} ha pasado a waiting')
                    yield env.timeout(1)  # Simulate waiting time for I/O
                print(f'{env.now}: El proceso {name} está listo para continuar')
        
        print(f'{env.now}: El proceso {name} ha terminado')
        self.RAM.put(required_memory)

def process_generator(env, os):
    for i in range(PROCESS_QUANTITY):  # Initially create 5 processes
        required_memory = random.randint(1, 10)
        total_instructions = random.randint(1, 10)
        env.process(os.process(f'Proceso {i}', required_memory, total_instructions))
        yield env.timeout(random.expovariate(1.0 / PROCESS_CREATION_INTERVAL))

# Set up and start the simulation
env = simpy.Environment()
os = OperatingSystem(env)
env.process(process_generator(env, os))
env.run(until=SIMULATION_TIME)
