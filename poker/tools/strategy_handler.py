import datetime
import json
import logging
import os
import re

from poker.tools.helper import get_config
from poker.tools.singleton import Singleton

log = logging.getLogger(__name__)

DATA_DIR = os.path.join(get_dir('codebase'), 'data')
TABLES_DIR = os.path.join(DATA_DIR, 'tables')
STRATEGIES_DIR = os.path.join(DATA_DIR, 'strategies')


class StrategyHandler(metaclass=Singleton):
    def __init__(self):
        self.current_strategy = None
        self.selected_strategy = None
        self.new_strategy_name = None
        self.modified = False

    def get_playable_strategy_list(self):
        strategies = []
        if not os.path.exists(STRATEGIES_DIR):
            return strategies
        for fname in os.listdir(STRATEGIES_DIR):
            if fname.startswith('strategy_') and fname.endswith('.json'):
                name = fname[len('strategy_'):-len('.json')].replace('_', ' ')
                strategies.append(name)
        return strategies

    def check_defaults(self):
        if 'initialFunds2' not in self.selected_strategy:
            self.selected_strategy['initialFunds2'] = self.selected_strategy['initialFunds']
        if 'use_relative_equity' not in self.selected_strategy:
            self.selected_strategy['use_relative_equity'] = 0
        if 'use_pot_multiples' not in self.selected_strategy:
            self.selected_strategy['use_pot_multiples'] = 0
        if 'opponent_raised_without_initiative_flop' not in self.selected_strategy:
            self.selected_strategy['opponent_raised_without_initiative_flop'] = 1
        if 'opponent_raised_without_initiative_turn' not in self.selected_strategy:
            self.selected_strategy['opponent_raised_without_initiative_turn'] = 1
        if 'opponent_raised_without_initiative_river' not in self.selected_strategy:
            self.selected_strategy['opponent_raised_without_initiative_river'] = 1
        if 'always_call_low_stack_multiplier' not in self.selected_strategy:
            self.selected_strategy['always_call_low_stack_multiplier'] = 8
        if 'differentiate_reverse_sheet' not in self.selected_strategy:
            self.selected_strategy['differentiate_reverse_sheet'] = 1
        if 'range_of_range' not in self.selected_strategy:
            self.selected_strategy['range_of_range'] = 0
        if 'out_multiplier' not in self.selected_strategy:
            self.selected_strategy['out_multiplier'] = 0
        if 'FlopBluffMaxEquity' not in self.selected_strategy:
            self.selected_strategy['FlopBluffMaxEquity'] = 100
        if 'TurnBluffMaxEquity' not in self.selected_strategy:
            self.selected_strategy['TurnBluffMaxEquity'] = 100
        if 'RiverBluffMaxEquity' not in self.selected_strategy:
            self.selected_strategy['RiverBluffMaxEquity'] = 100
        if 'flop_betting_condidion_1' not in self.selected_strategy:
            self.selected_strategy['flop_betting_condidion_1'] = 1
        if 'turn_betting_condidion_1' not in self.selected_strategy:
            self.selected_strategy['turn_betting_condidion_1'] = 1
        if 'river_betting_condidion_1' not in self.selected_strategy:
            self.selected_strategy['river_betting_condidion_1'] = 1
        if 'flop_bluffing_condidion_1' not in self.selected_strategy:
            self.selected_strategy['flop_bluffing_condidion_1'] = 1
        if 'turn_bluffing_condidion_1' not in self.selected_strategy:
            self.selected_strategy['turn_bluffing_condidion_1'] = 0
        if 'turn_bluffing_condidion_2' not in self.selected_strategy:
            self.selected_strategy['turn_bluffing_condidion_2'] = 1
        if 'river_bluffing_condidion_1' not in self.selected_strategy:
            self.selected_strategy['river_bluffing_condidion_1'] = 0
        if 'river_bluffing_condidion_2' not in self.selected_strategy:
            self.selected_strategy['river_bluffing_condidion_2'] = 1
        if 'collusion' not in self.selected_strategy:
            self.selected_strategy['collusion'] = 1

        if 'max_abs_fundchange' not in self.selected_strategy:
            self.selected_strategy['max_abs_fundchange'] = 4
        if 'RiverCheckDeceptionMinEquity' not in self.selected_strategy:
            self.selected_strategy['RiverCheckDeceptionMinEquity'] = .1
        if 'TurnCheckDeceptionMinEquity' not in self.selected_strategy:
            self.selected_strategy['TurnCheckDeceptionMinEquity'] = .1
        if 'pre_flop_equity_reduction_by_position' not in self.selected_strategy:
            self.selected_strategy['pre_flop_equity_reduction_by_position'] = 0.01
        if 'pre_flop_equity_increase_if_bet' not in self.selected_strategy:
            self.selected_strategy['pre_flop_equity_increase_if_bet'] = 0.20
        if 'pre_flop_equity_increase_if_call' not in self.selected_strategy:
            self.selected_strategy['pre_flop_equity_increase_if_call'] = 0.10
        if 'preflop_override' not in self.selected_strategy:
            self.selected_strategy['preflop_override'] = 1
        if 'gather_player_names' not in self.selected_strategy:
            self.selected_strategy['gather_player_names'] = 0
        if 'range_utg0' not in self.selected_strategy:
            self.selected_strategy['range_utg0'] = 0.2
        if 'range_utg1' not in self.selected_strategy:
            self.selected_strategy['range_utg1'] = 0.2
        if 'range_utg2' not in self.selected_strategy:
            self.selected_strategy['range_utg2'] = 0.2
        if 'range_utg3' not in self.selected_strategy:
            self.selected_strategy['range_utg3'] = 0.2
        if 'range_utg4' not in self.selected_strategy:
            self.selected_strategy['range_utg4'] = 0.2
        if 'range_utg5' not in self.selected_strategy:
            self.selected_strategy['range_utg5'] = 0.2
        if 'range_multiple_players' not in self.selected_strategy:
            self.selected_strategy['range_multiple_players'] = 0.2
        if 'minimum_bet_size' not in self.selected_strategy:
            self.selected_strategy['minimum_bet_size'] = 3
        if 'antibluff_percentage' not in self.selected_strategy:
            self.selected_strategy['antibluff_percentage'] = 0
        if 'range_preflop' not in self.selected_strategy:
            self.selected_strategy['range_preflop'] = 100
        if 'increased_preflop_betting' not in self.selected_strategy:
            self.selected_strategy['increased_preflop_betting'] = 1

    def read_strategy(self, strategy_override=''):
        config = get_config()
        last_strategy = config.config.get('main', 'last_strategy')
        self.current_strategy = last_strategy if strategy_override == '' else strategy_override
        safe_name = self.current_strategy.replace(' ', '_')

        fpath = os.path.join(STRATEGIES_DIR, f'strategy_{safe_name}.json')
        if not os.path.exists(fpath):
            log.error(f"Strategy '{self.current_strategy}' not found locally: {fpath}")
            fpath = os.path.join(STRATEGIES_DIR, 'strategy_Official_1.json')
            self.current_strategy = 'Official 1'
            if not os.path.exists(fpath):
                raise FileNotFoundError(
                    f"Default strategy not found. Place strategy JSON files in {STRATEGIES_DIR}")

        with open(fpath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        if isinstance(data, list):
            self.selected_strategy = data[0]
        else:
            self.selected_strategy = data
        self.check_defaults()
        return True

    def save_strategy(self, strategy_dict):
        os.makedirs(STRATEGIES_DIR, exist_ok=True)
        name = strategy_dict.get('Strategy', 'custom')
        safe_name = name.replace(' ', '_')
        fpath = os.path.join(STRATEGIES_DIR, f'strategy_{safe_name}.json')
        with open(fpath, 'w', encoding='utf-8') as f:
            json.dump([strategy_dict], f, indent=2, default=str)
        log.info(f"Strategy saved to {fpath}")
        return True

    def update_strategy(self, strategy):
        if '_id' in strategy:
            del strategy['_id']
        return self.save_strategy(strategy)

    def save_strategy_genetic_algorithm(self):
        m = re.search(r'([a-zA-Z?-_]+)([0-9]+)', self.current_strategy)
        stringPart = m.group(1)
        numberPart = int(m.group(2))
        numberPart += 1
        suffix = "_" + str(datetime.datetime.now())
        self.new_strategy_name = stringPart + str(numberPart) + suffix
        self.selected_strategy['Strategy'] = self.new_strategy_name
        self.current_strategy = self.new_strategy_name
        return self.save_strategy(self.selected_strategy)

    def modify_strategy(self, elementName, change):
        self.selected_strategy[elementName] = str(
            round(float(self.selected_strategy[elementName]) + change, 2))
        self.modified = True