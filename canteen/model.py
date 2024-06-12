from mesa import Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector
from .agents import Customer, StaticElement
import random

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
        self.cashier_location = [(2, 19), (6, 19), (10, 19), (14, 19), (18, 19), (22, 19), (3, 19), (7, 19), (11, 19), (15, 19), (19, 19), (23, 19), (4, 19), (8, 19), (12, 19), (16, 19), (20, 19), (24, 19), (5, 19), (9, 19), (13, 19), (17, 19), (21, 19), (25, 19)]
        self.exit_location = [(43, i) for i in range(1, 23)]
        self.store = [(i+2, 20) for i in range(24)] + [(i+2, 21) for i in range(24)] + [(i+2, 22) for i in range(24)]

        self.dining_areas = [(3 * (i + 1), 14) for i in range(11)] + [(3 * (j + 1) + 1, 14) for j in range(11)] + \
                            [(3 * (i + 1), 15) for i in range(11)] + [(3 * (j + 1) + 1, 15) for j in range(11)] + \
                            [(3 * (i + 1), 10) for i in range(11)] + [(3 * (j + 1) + 1, 10) for j in range(11)] + \
                            [(3 * (i + 1), 11) for i in range(11)] + [(3 * (j + 1) + 1, 11) for j in range(11)] + \
                            [(33, 2), (33, 3), (34, 2), (34, 3), (33, 5), (33, 6), (34, 5), (34, 6),(33, 20), (34, 20), (33, 21), (34, 21), (31, 20), (30, 20), (31, 21), (30, 21)] + \
                            [(6, i + 3) for i in range(4)] + [(7, 3), (7, 6)] + [(8, 3), (8, 6)] + [(9, i + 3) for i in range(4)] + \
                            [(13, i + 3) for i in range(4)] + [(14, 3), (14, 6)] + [(15, 3), (15, 6)] + [(16, i + 3) for i in range(4)] + \
                            [(20, i + 3) for i in range(4)] + [(21, 3), (21, 6)] + [(22, 3), (22, 6)] + [(23, i + 3) for i in range(4)] + \
                            [(27, i + 3) for i in range(4)] + [(28, 3), (28, 6)] + [(29, 3), (29, 6)] + [(30, i + 3) for i in range(4)]
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
        self.next_customer_time = self.current_time + self.random_time_between(0, 720)

    def find_empty_seat(self, current_pos):
        empty_seats = [seat for seat in self.dining_areas if self.is_seat_empty_for_customer(seat)]
        if not empty_seats:
            return None
        return random.choice(empty_seats) if random.choice([True, False]) else min(empty_seats, key=lambda x: self.manhattan_distance(current_pos, x))

    def find_empty_queue(self, current_pos):
        empty_queues = [queue for queue in self.cashier_location if self.grid.is_cell_empty(queue)]
        if not empty_queues:
            return None
        # Randomly choose an empty queue
        return random.choice(empty_queues)

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
