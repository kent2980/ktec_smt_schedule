from dataclasses import dataclass
from datetime import date
from typing import Dict


@dataclass
class LotInfo:
    """
    Lot情報

    Attributes:
        machine_name (str): マシン名
        model_name (str): モデル名
        board_name (str): 基板名
        lot_number (str): 指図
        model_code (str): Y番
        default_date (date): 基準日
        volume (int): 台数
        line_code (str): 棚番
        productions (List[Dict[date, int]]): 生産予定
    """

    machine_name: str
    "**マシン名**"
    model_name: str
    "**モデル名**"
    board_name: str
    "**基板名**"
    lot_number: str
    "**指図**"
    model_code: str
    "**Y番**"
    default_date: date
    "**基準日**"
    volume: int
    "**台数**"
    rest_volume: int
    "**残台数**"
    line_code: str
    "**棚番**"
    productions: Dict[str, int]
    "**生産予定**"
    divisions_volume: int
    "**分割台数**"

    def __init__(self):
        self.machine_name = ""
        self.model_name = ""
        self.board_name = ""
        self.lot_number = ""
        self.model_code = ""
        self.default_date = None
        self.volume = 0
        self.rest_volume = 0
        self.line_code = ""
        self.productions = {}
        self.divisions_volume = 0
