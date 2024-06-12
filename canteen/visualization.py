from .agents import Customer, StaticElement

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