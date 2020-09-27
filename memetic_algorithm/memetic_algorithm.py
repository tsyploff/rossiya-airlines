import numpy as np 
import pandas as pd

class Population():
    """docstring for Population"""

    def __init__(self, population=None, #можно передать конкретную популяцию
                 population_size=10,    #размер популяции
                 random_state=42,       #фиксируем seed, если инициализируется случайная популяция
                 number_of_vectors=10,  #количество векторов n
                 vectors_dimension=10,  #размерность векторов m
                 number_of_groups=2,    #количество групп, на которое мы делим вектора k
                 crossover_percent=0.85,  #процент детей в новом поколении
                 mutation_probability=0.1 #вероятность мутации гена
                ):
        '''Инициализирует популяцию'''
        if type(population) != type(None): #по умолчанию инициализирует случайную популяцию
            self.population = population
            self.population_size = population.shape[0]
        else:
            np.random.seed(random_state)
            self.population = np.random.randint(0, high=number_of_groups, size=(population_size, number_of_vectors))
            self.population_size = population_size

        self.random_state = random_state
        self.fitness_values = np.zeros(shape=population_size)
        self.number_of_groups  = number_of_groups
        self.vectors_dimension = vectors_dimension
        self.number_of_vectors = number_of_vectors
        self.crossover_percent = crossover_percent
        self.mutation_probability = mutation_probability

    def evaluate_fitness_values(self, vectors):
        '''Вычисляет fitness_values хромосом'''
        self.fitness_values = []
        for chromosome in self.population:
            sums = np.array([vectors[chromosome == l].sum(axis=0) for l in range(self.number_of_groups)])
            self.fitness_values.append(np.abs(sums.max(axis=0) - sums.min(axis=0)).max())
        self.fitness_values = np.array(self.fitness_values)
        return self.fitness_values

    def sort(self, vectors):
        data = pd.DataFrame(self.population, columns=np.arange(self.number_of_vectors))
        data['fitness_values'] = self.evaluate_fitness_values(vectors)
        data = data.sort_values(by=['fitness_values'])
        self.population = data[np.arange(self.number_of_vectors)].values
        self.fitness_values = data['fitness_values'].values
        return self
        
    def mutate(self):
        '''Осуществляет операцию мутации со всей популяцией'''
        return np.where(np.random.random(size=(self.population_size, self.number_of_vectors)) <= self.mutation_probability, 
                        np.random.randint(0, high=self.number_of_groups, size=(self.population_size, self.number_of_vectors)), 
                        self.population)

    def crossover(self):
        '''Осуществляет операцию мутации со всей популяцией'''
        generation = []
        for i in range(self.population_size - 1):
            crossover_point = np.random.randint(1, high=self.number_of_vectors-1, size=1)
            generation.append(np.hstack((self.population[i, :crossover_point[0]], self.population[i + 1, crossover_point[0]:])))
            generation.append(np.hstack((self.population[i + 1, :crossover_point[0]], self.population[i, crossover_point[0]:])))
        return np.array(generation)

    def next_generation(self, vectors):
        '''Осуществляет переход к новому поколению'''
        new_generation = Population(population=self.crossover(), number_of_vectors=vectors.shape[0]).sort(vectors)
        self.sort(vectors)
        number = int(self.crossover_percent*self.population_size)
        self.population = np.vstack((new_generation.population[:number], self.population[:self.population_size - number]))
        self.population = self.mutate()
        self.local_search_2_change(vectors).sort(vectors)
        return self

    def local_search_2_change(self, vectors):
        for i in range(self.population_size):
            chromosome = self.population[i]
            i1, i2 = np.random.choice(np.arange(self.number_of_vectors), size=2, replace=False)
            new_chromosome = chromosome.copy()
            new_chromosome[i1] = chromosome[i2]
            new_chromosome[i2] = chromosome[i1]
            sums = np.array([vectors[new_chromosome == l].sum(axis=0) for l in range(self.number_of_groups)])
            t = np.abs(sums.max(axis=0) - sums.min(axis=0)).max()
            if t < self.fitness_values[i]:
                self.population[i] = new_chromosome
                self.fitness_values[i] = t
        return self

class Memetic():

    count = 0
    solutions = {}

    def solve(vectors, popul, number_of_steps=10):
        population = Population(population=popul.population,              
                                population_size=popul.population_size,    
                                random_state=popul.random_state,          
                                number_of_vectors=popul.number_of_vectors,
                                vectors_dimension=popul.vectors_dimension,
                                number_of_groups=popul.number_of_groups,  
                                crossover_percent=popul.crossover_percent,
                                mutation_probability=popul.mutation_probability 
                               ).sort(vectors)
        best  = population.population[0]
        value = population.fitness_values[0]
        story = []
        for i in range(number_of_steps):
            population = population.next_generation(vectors)
            if population.fitness_values[0] < value:
                best  = population.population[0]
                value = population.fitness_values[0]
            story.append(value)

        Memetic.count += 1
        Memetic.solutions[Memetic.count] = {'value' : value, 
                                            'objective function story' : np.array(story), 
                                            'solution' : best, 
                                            'start population' : popul,
                                            'end population' : population}
        print('Решение записано в Memetic.solutions, идентификатор: {}'.format(Memetic.count))
        return value, best
