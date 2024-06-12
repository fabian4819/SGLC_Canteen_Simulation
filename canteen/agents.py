from mesa import Agent
import random

class Customer(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.state = "entering"  # entering, queuing, ordering, eating, exiting
        self.steps_eating = 0
        self.steps_queuing = 0

    def move_towards(self, destination):
        current_pos = self.pos
        direction_vector = (destination[0] - current_pos[0], destination[1] - current_pos[1])
        step_direction = (int(direction_vector[0] / max(1, abs(direction_vector[0]))), int(direction_vector[1] / max(1, abs(direction_vector[1]))))
        new_position = (current_pos[0] + step_direction[0], current_pos[1] + step_direction[1])
        if not self.model.grid.out_of_bounds(new_position) and new_position not in self.model.boundaries and new_position not in self.model.big_table and new_position not in self.model.store:
            if self.state != "eating" or self.state != "entering" or self.model.grid.is_cell_empty(new_position):
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
        if current_hour > 16 or current_hour < 8:
            self.state = "exiting"
        elif 8 <= current_hour <= 16:
            empty_queue = self.model.find_empty_queue(self.pos)
            if empty_queue:
                self.move_towards(empty_queue)
                if self.pos == empty_queue:
                    self.state = "ordering"
            else:
                self.move()

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