from .main import Charts

def start():
    return Charts()

config = [{
    'name': 'display_charts_providers',
    'groups': [
        {
            'label': 'Charts',
            'description': 'Displays selected charts on the home page',
            'type': 'list',
            'name': 'charts_providers',
            'tab': 'automation',
            'options': [],
        },
    ],
}]