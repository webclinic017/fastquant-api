import pandas as pd
from contracts.v1.request import DashboardSubscriptionConfiguration
from fastapi import WebSocket, WebSocketDisconnect
from typing import List, Dict, Tuple, Text

from .router_resolver import RouterResolver
from util import Singleton
import asyncio
from collections import deque

router = RouterResolver().router

class ConnectionManager(metaclass=Singleton):
    def __init__(self):
        self.active_connections: List[Tuple(WebSocket, DashboardSubscriptionConfiguration)] = []

    async def register(self, websocket: WebSocket, cfg: DashboardSubscriptionConfiguration):
        self.active_connections.append((websocket, cfg))

    def unregister(self, websocket: WebSocket):
        self.active_connections = [x for x in self.active_connections if x[0] != websocket]

    @staticmethod
    async def send_update(websocket: WebSocket, configuration: DashboardSubscriptionConfiguration, publisher_name: str, data):
        # filter based on connection config
        if publisher_name not in configuration.columns:
            return

        wanted_columns_from_publisher = configuration.columns[publisher_name]
        filtered_data = {k: data[k] for k in wanted_columns_from_publisher}
        await websocket.send_json({publisher_name: filtered_data})

    async def broadcast_updates(self, publisher_name: str, data):
        futures = []
        for websocket, configuration in self.active_connections:
            future = self.send_update(websocket, configuration, publisher_name, data)
            futures.append(future)

        await asyncio.gather(*futures)
    
manager = ConnectionManager()

class DataBuffers(metaclass=Singleton):
    def __init__(self):
        self.buffers = {"test":{"col1":[1,2,3,4,5,6,7,8],"col2":[2,3,4,5,1,1,1,1]}}

    @property
    def all_data(self):
        return self.buffers

    def register_publisher(self, name):
        if name not in self.buffers:
            self.buffers[name] = {}
    
    def append_data(self, name, columns: Dict[Text, List]):
        buf_cols = self.buffers[name]

        for colname, colval in columns.items():
            if colname not in buf_cols:
                buf_cols[colname] = deque(maxlen=10000)
            
            buf_cols[colname].extend(colval)

buffers = DataBuffers()

@router.websocket('/dashboard/publish/{name}')
async def dashboard_publish(websocket: WebSocket, name: str = None):
    if name == None or len(name) == 0:
        return

    await websocket.accept()
    buffers.register_publisher(name)
    try:
        while True:
            data = await websocket.receive_json()
            await manager.broadcast_updates(name, data)
            buffers.append_data(name, data)
    except WebSocketDisconnect:
        pass
        # notify subscribers that publisher / source went offline ?

@router.websocket('/dashboard/subscribe')
async def dashboard_subscribe(websocket: WebSocket, 
                                load_history: bool = False):
    await websocket.accept()
    config_json = await websocket.receive_json()
    subscription_config = DashboardSubscriptionConfiguration.parse_obj(config_json)
    await manager.register(websocket, subscription_config)
    try:
        if load_history:
            for publisher_name, publisher_data in buffers.all_data.items():
                await ConnectionManager.send_update(websocket, subscription_config, publisher_name, publisher_data)
        while True:
            await asyncio.sleep(30)
    except WebSocketDisconnect:
        manager.unregister(websocket)

@router.get('/dashboard/ping')
def dash_ping():
    return 'pong'

@router.get('/dashboard/data')
def dashboard_data():
    response = {}
    for publisher_name, coldict in buffers.all_data.items():
        response[publisher_name] = {}
        for column_name, q in coldict.items():
            response[publisher_name][column_name] = [x for x in q] # unwrap deques to list

    return response
            