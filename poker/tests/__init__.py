import inspect
import logging
import os
import sys
from unittest.mock import MagicMock

import pandas as pd
from PIL import Image

from poker import main
from poker.tools.mongo_manager import MongoManager
from poker.tools.strategy_handler import StrategyHandler

currentdir = os.path.dirname(os.path.abspath(
    inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'data')
PREFLOP_PATH = os.path.join(DATA_DIR, 'decisionmaker', 'preflop.xlsx')


def init_table(file, round_number=0, strategy='Official 1', table_scraper_name='Official GGPoker 6player'):
    logger = logging.getLogger('tester')
    gui_signals = MagicMock()
    p = StrategyHandler()
    p.read_strategy(strategy_override=strategy)
    h = main.History()
    h.preflop_sheet = pd.read_excel(PREFLOP_PATH, sheet_name=None, engine='openpyxl')
    game_logger = MagicMock()
    mongo = MongoManager()
    table_dict = mongo.get_table(table_scraper_name)
    t = main.TableScreenBased(p, {}, gui_signals, game_logger, 0.0)

    current_file_dir = os.path.dirname(os.path.abspath(__file__))
    adjusted_path = os.path.join(current_file_dir, 'screenshots', file)
    t.entireScreenPIL = Image.open(adjusted_path)
    t.get_top_left_corner(p)
    t.get_dealer_position()
    t.get_my_funds(h, p)
    t.get_my_cards_nn()
    # t.get_table_cards_nn(h)
    t.get_round_number(h)
    h.round_number = round_number
    t.init_get_other_players_info()
    t.get_other_player_names(p)
    t.get_other_player_funds(p)
    t.get_other_player_pots()
    t.get_other_player_status(p, h)
    t.check_for_checkbutton()
    t.check_for_call()
    t.check_for_betbutton()
    t.check_for_allincall()
    t.get_current_call_value(p)
    t.get_current_bet_value(p)
    p = MagicMock()
    gui_signals = MagicMock()
    t.totalPotValue = 0.5
    t.equity = 0.5
    return t, p, gui_signals, h, logger