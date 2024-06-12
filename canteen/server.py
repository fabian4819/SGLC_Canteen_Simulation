from mesa.visualization.modules import CanvasGrid, ChartModule
from mesa.visualization.ModularVisualization import ModularServer
from .model import CanteenModel
from .visualization import customer_portrayal

def run_server():
    width, height = 44, 24
    grid = CanvasGrid(customer_portrayal, width, height, width * 20, height * 20)

    chart = ChartModule([{"Label": "Entering", "Color": "green"},
                         {"Label": "Queuing", "Color": "yellow"},
                         {"Label": "Ordering", "Color": "blue"},
                         {"Label": "Eating", "Color": "red"}],
                        data_collector_name='datacollector')

    server = ModularServer(CanteenModel,
                           [grid, chart],
                           "SGLC Canteen Model Simulation",
                           {"width": width, "height": height})

    server.port = 8521
    server.launch()