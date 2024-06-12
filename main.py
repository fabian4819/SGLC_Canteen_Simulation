from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector
from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import ChartModule
import random
import matplotlib.pyplot as plt
import pandas as pd


class Customer(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.state = "entering"  # entering, queuing, ordering, eating, exiting
        self.steps_eating = 0
        self.steps_queuing = 0

    def move_towards(self, destination):
        current_pos = self.pos
        direction_vector = (destination[0] - current_pos[0], destination[1] - current_pos[1])
        step_direction = (int(direction_vector[0] / max(1, abs(direction_vector[0]))),
                          int(direction_vector[1] / max(1, abs(direction_vector[1]))))
        new_position = (current_pos[0] + step_direction[0], current_pos[1] + step_direction[1])
        if not self.model.grid.out_of_bounds(new_position) and new_position not in self.model.boundaries and new_position not in self.model.big_table and new_position not in self.model.store:
            if self.state != "eating" or self.model.grid.is_cell_empty(new_position):
                self.model.grid.move_agent(self, new_position)
    
    def move(self):
        possible_steps = self.model.grid.get_neighborhood(self.pos, moore=True, include_center=False)
        free_steps = [step for step in possible_steps if self.model.grid.is_cell_empty(step)]
        if free_steps:
            new_position = self.random.choice(free_steps)
            self.model.grid.move_agent(self, new_position)

    def step(self):
        if self.state == "entering":
            self.enter_canteen()
        elif self.state == "queuing":
            self.queue_for_food()
        elif self.state == "ordering":
            self.order_food()
        elif self.state == "eating":
            self.eat_food()
        elif self.state == "exiting":
            self.exit_canteen()

    def enter_canteen(self):
        current_hour = int(self.model.current_time)
        if self.model.current_time > 16:
            self.state = "exiting"
        elif 8 <= current_hour < 16:
            empty_queue = self.model.find_empty_queue(self.pos)
            if empty_queue:
                self.move_towards(empty_queue)
                if self.pos == empty_queue:
                    self.state = "ordering"
        else:
            self.state = "exiting"

    def queue_for_food(self):
        empty_queue = self.model.find_empty_queue(self.pos)
        if empty_queue:
            self.move_towards(empty_queue)
            if self.pos == empty_queue:
                self.state = "ordering"
        else:
            self.move()  # If no empty queue is found, move randomly

    def order_food(self):
        self.steps_queuing += 1
        if self.steps_queuing >= random.gauss(2, 1):
            self.steps_queuing = 0
            empty_seat = self.model.find_empty_seat(self.pos)
            if empty_seat:
                self.move_towards(empty_seat)
                if self.pos == empty_seat:
                    self.state = "eating"
            else:
                self.move()  # If no empty seat is found, move randomly

    def eat_food(self):
        if self.steps_eating < random.randint(20, 30):  # Simulate eating for 20 to 30 steps (minutes)
            self.steps_eating += 1
        else:
            self.state = "exiting"

    def exit_canteen(self):
        self.move_towards(self.model.exit_location[random.randint(0, len(self.model.exit_location) - 1)])
        if self.pos in self.model.exit_location:
            self.model.grid.remove_agent(self)
            self.model.schedule.remove(self)


class StaticElement(Agent):
    def __init__(self, unique_id, model, element_type):
        super().__init__(unique_id, model)
        self.element_type = element_type

    def step(self):
        pass


class CanteenModel(Model):
    def __init__(self, width, height):
        super().__init__()
        self.grid = MultiGrid(width, height, False)
        self.schedule = RandomActivation(self)
        self.current_id = 0
        self.start_time = 8  # Simulation starts at 6 AM
        self.end_time = 18  # Simulation ends at 6 PM
        self.current_time = self.start_time

        self.steps_since_last_customer = 0

        self.entry_point = (41, random.randint(0, 22))
        self.cashier_location = [(2, 19), (6, 19), (10, 19), (14, 19), (18, 19), (22, 19), (3, 19), (7, 19), (11, 19),
                                 (15, 19), (19, 19), (23, 19), (4, 19), (8, 19), (12, 19), (16, 19), (20, 19),
                                 (24, 19), (5, 19), (9, 19), (13, 19), (17, 19), (21, 19), (25, 19)]
        self.exit_location = [(43, i) for i in range(1, 23)]
        self.store = [(i+2, 20) for i in range(24)] + [(i+2, 21) for i in range(24)] + [(i+2, 22) for i in range(24)]

        self.dining_areas = [(3 * (i + 1), 14) for i in range(11)] + [(3 * (j + 1) + 1, 14) for j in range(11)] + \
                            [(3 * (i + 1), 15) for i in range(11)] + [(3 * (j + 1) + 1, 15) for j in range(11)] + \
                            [(3 * (i + 1), 10) for i in range(11)] + [(3 * (j + 1) + 1, 10) for j in range(11)] + \
                            [(3 * (i + 1), 11) for i in range(11)] + [(3 * (j + 1) + 1, 11) for j in range(11)] + \
                            [(33, 2), (33, 3), (34, 2), (34, 3),
                             (33, 5), (33, 6), (34, 5), (34, 6),(33, 20), (34, 20), (33, 21), (34, 21), (31, 20),
                             (30, 20), (31, 21), (30, 21)] + \
                            [(6, i + 3) for i in range(4)] + [(7, 3), (7, 6)] + [(8, 3), (8, 6)] + [(9, i + 3) for i in
                                                                                                      range(4)] + \
                            [(13, i + 3) for i in range(4)] + [(14, 3), (14, 6)] + [(15, 3), (15, 6)] + [(16, i + 3) for i
                                                                                                         in range(
                                4)] + \
                            [(20, i + 3) for i in range(4)] + [(21, 3), (21, 6)] + [(22, 3), (22, 6)] + [(23, i + 3) for i
                                                                                                          in range(
                                4)] + \
                            [(27, i + 3) for i in range(4)] + [(28, 3), (28, 6)] + [(29, 3), (29, 6)] + [(30, i + 3) for i
                                                                                                          in range(
                                4)]
        self.big_table = [(7, 4), (7, 5), (8, 4), (8, 5)] + [(14, 4), (14, 5), (15, 4), (15, 5)] + [(21, 4), (21, 5), (22, 4), (22, 5)] + [(28, 4), (28, 5), (29, 4), (29, 5)]
        self.boundaries = [(i, 0) for i in range(width)] + [(i, 23) for i in range(44)] +\
                          [(0, j) for j in range(height)] 

        self.next_customer_time = self.random_time_between(0, 60)

        self.datacollector = DataCollector(
            agent_reporters={"State": "state"},
            model_reporters={"Current Time": "current_time",
                             "Formatted Time": lambda m: m.get_time_string(),
                             "Entering": lambda m: self.count_customers_by_state("entering"),
                             "Queuing": lambda m: self.count_customers_by_state("queuing"),
                             "Ordering": lambda m: self.count_customers_by_state("ordering"),
                             "Eating": lambda m: self.count_customers_by_state("eating"),
                             "Exiting": lambda m: self.count_customers_by_state("exiting")}
        )

        for boundary in self.boundaries:
            self.add_static_element(boundary, "boundary")

        for dining_area in self.dining_areas:
            self.add_static_element(dining_area, "dining_area")

        for exit_loc in self.exit_location:
            self.add_static_element(exit_loc, "exit_location")
        
        for store_loc in self.store:
            self.add_static_element(store_loc, "store")
            
        for big_table_loc in self.big_table:
            self.add_static_element(big_table_loc, "big_table")
        
        

    def add_static_element(self, pos, element_type):
        element = StaticElement(self.next_id(), self, element_type)
        self.grid.place_agent(element, pos)
        self.schedule.add(element)

    def random_time_between(self, start, end):
        return random.uniform(start, end)

    def add_customer(self):
        c = Customer(self.current_id, self)
        self.schedule.add(c)
        self.grid.place_agent(c, (41, random.randint(0, 22)))
        self.current_id += 1
        self.next_customer_time = self.current_time + self.random_time_between(0, 60)

    def find_empty_seat(self, current_pos):
        empty_seats = [seat for seat in self.dining_areas if self.is_seat_empty_for_customer(seat)]
        if not empty_seats:
            return None
        return random.choice(empty_seats) if random.choice([True, False]) else min(empty_seats,
                                                                                   key=lambda x: self.manhattan_distance(current_pos, x))

    def find_empty_queue(self, current_pos):
        empty_queues = [queue for queue in self.cashier_location if self.grid.is_cell_empty(queue)]
        if not empty_queues:
            return None
        return random.choice(empty_queues) if random.choice([True, False]) else min(empty_queues,
                                                                                    key=lambda x: self.manhattan_distance(
                                                                                        current_pos, x))

    def manhattan_distance(self, pos1, pos2):
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

    def get_time_string(self):
        total_minutes = self.current_time * 60
        hours = int(total_minutes // 60)
        minutes = int(total_minutes % 60)
        return f"{hours:02d}:{minutes:02d}"

    def count_customers_by_state(self, state):
        count = 0
        for agent in self.schedule.agents:
            if isinstance(agent, Customer) and agent.state == state:
                count += 1
        return count

    def step(self):
        self.datacollector.collect(self)
        self.schedule.step()

        current_hour = int(self.current_time)
        if 8 <= current_hour <= 16:
            if self.current_time >= self.next_customer_time:
                self.add_customer()

        self.current_time += 1 / 60  # Assume one step is one minute

        if self.current_time >= self.end_time:
            self.running = False

        self.steps_since_last_customer += 1

        if self.steps_since_last_customer >= 1:
            if 7 <= current_hour <= 16:
                if 11 <= current_hour < 13:
                    self.add_customer()
                elif current_hour == 9:
                    self.add_customer()
                self.add_customer()
            self.steps_since_last_customer = 0

        # Print the current time in HH:MM format
        print(self.get_time_string())
        
    def is_seat_empty_for_customer(self, pos):
        # Check if the cell at `pos` contains any Customer agents
        cell_contents = self.grid.get_cell_list_contents(pos)
        for agent in cell_contents:
            if isinstance(agent, Customer):
                return False
        return True


def customer_portrayal(agent):
    if isinstance(agent, Customer):
        portrayal = {"Shape": "circle",
                     "Filled": "true",
                     "r": 0.5}
        if agent.state == "entering":
            portrayal["Color"] = "green"
            portrayal["Layer"] = 1  # Ensure this is higher than StaticElement layer
        elif agent.state == "queuing":
            portrayal["Color"] = "yellow"
            portrayal["Layer"] = 1
        elif agent.state == "ordering":
            portrayal["Color"] = "blue"
            portrayal["Layer"] = 1
        elif agent.state == "eating":
            portrayal["Color"] = "red"
            portrayal["Layer"] = 1
        elif agent.state == "exiting":
            portrayal["Color"] = "gray"
            portrayal["Layer"] = 1
        return portrayal

    elif isinstance(agent, StaticElement):
        portrayal = {"Shape": "rect",
                     "w": 1,
                     "h": 1,
                     "Filled": "true",
                     "Layer": 0}  # Static elements should be in a lower layer
        if agent.element_type == "boundary":
            portrayal["Color"] = "black"
            portrayal["Layer"] = 0
        elif agent.element_type == "cashier_location":
            portrayal["Color"] = "lightyellow"
            portrayal["Layer"] = 0
        elif agent.element_type == "dining_area":
            portrayal["Color"] = "lightblue"
            portrayal["Layer"] = 0
        elif agent.element_type == "exit_location":
            portrayal["Color"] = "orange"
            portrayal["Layer"] = 0
        elif agent.element_type == "store":
            portrayal["Color"] = "yellow"
            portrayal["Layer"] = 0
        elif agent.element_type == "big_table":
            portrayal["Color"] = "blue"
            portrayal["Layer"] = 0
        return portrayal


width, height = 44, 24
grid = CanvasGrid(customer_portrayal, width, height, width * 20, height * 20)

chart = ChartModule([{"Label": "Entering", "Color": "green"},
                     {"Label": "Queuing", "Color": "yellow"},
                     {"Label": "Ordering", "Color": "blue"},
                     {"Label": "Eating", "Color": "red"}],
                    data_collector_name='datacollector')

server = ModularServer(CanteenModel,
                       [grid, chart],
                       "Canteen Model",
                       {"width": width, "height": height})

server.port = 8521

if __name__ == "__main__":
    server.launch()
