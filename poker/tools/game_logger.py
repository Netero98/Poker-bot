import datetime
import json
import logging
import os
import threading
from collections.abc import Iterable

import pandas as pd

from poker.tools.helper import COMPUTER_NAME, get_dir
from poker.tools.mongo_manager import MongoManager
from poker.tools.singleton import Singleton

log = logging.getLogger(__name__)

_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
LOG_DIR = os.path.join(_PROJECT_ROOT, 'log', 'games')


def _ensure_log_dir():
    os.makedirs(LOG_DIR, exist_ok=True)


class GameLogger(metaclass=Singleton):
    def __init__(self, *args, **kwargs):
        self.d = {}
        self.FinalDataFrame = None

    def isIterable(self, x):
        if isinstance(x, Iterable) and not isinstance(x, str):
            return x
        return [x]

    def get_played_strategy_list(self):
        strategies_dir = os.path.join(get_dir('codebase'), 'data', 'strategies')
        result = []
        if os.path.exists(strategies_dir):
            for fname in os.listdir(strategies_dir):
                if fname.startswith('strategy_') and fname.endswith('.json'):
                    result.append(fname[len('strategy_'):-len('.json')].replace('_', ' '))
        return result

    def write_log_file(self, p, h, t, d):
        hDict = {}
        tDict = {}
        dDict = {}
        pDict = {}

        for key, val in p.selected_strategy.items():
            pDict[key] = val
        for key, val in vars(h).items():
            hDict[key] = " ".join(str(ele) for ele in self.isIterable(val))
        for key, val in vars(t).items():
            if len(" ".join(str(ele) for ele in self.isIterable(val))) < 50:
                tDict[key] = " ".join(str(ele) for ele in self.isIterable(val))
        for key, val in vars(d).items():
            if len(" ".join(str(ele) for ele in self.isIterable(val))) < 20:
                dDict[key] = " ".join(str(ele) for ele in self.isIterable(val))

        pDict['computername'] = COMPUTER_NAME

        Dh = pd.DataFrame(hDict, index=[0])
        Dt = pd.DataFrame(tDict, index=[0])
        Dd = pd.DataFrame(dDict, index=[0])
        Dp = pd.DataFrame(pDict, index=[0])

        self.FinalDataFrame = pd.concat([Dd, Dt, Dh, Dp], axis=1)
        rec = self.FinalDataFrame.to_dict('records')[0]
        rec['other_players'] = t.other_players
        rec['logging_timestamp'] = str(datetime.datetime.utcnow())
        if 'logger' in rec:
            del rec['logger']

        t_log_db = threading.Thread(name='write_log', target=self._write_round_log, args=[rec])
        t_log_db.daemon = True
        t_log_db.start()

    def mark_last_game(self, t, h, p):
        outcome = "na"
        if t.myFundsChange > 0:
            outcome = "Won"
            h.wins += 1
            h.totalGames += 1
        elif t.myFundsChange < 0:
            outcome = "Lost"
            h.losses += 1
            h.totalGames += 1
        elif t.myFundsChange == 0:
            outcome = "Neutral"
            h.totalGames += 1
        if h.histGameStage != '':
            summary_dict = {'rounds': []}
            mongo = MongoManager()
            rounds = mongo.get_rounds(h.lastGameID)
            for i, _round in enumerate(rounds):
                round_name_value = {
                    'round_number': str(i),
                    'round_values': _round
                }
                summary_dict['rounds'].append(round_name_value)

            summary_dict['GameID'] = h.lastGameID
            summary_dict['ComputerName'] = COMPUTER_NAME
            summary_dict['logging_timestamp'] = str(datetime.datetime.now())
            summary_dict['FinalOutcome'] = outcome
            summary_dict['FinalStage'] = h.histGameStage
            summary_dict['FinalFundsChange'] = t.myFundsChange
            summary_dict['FinalFundsChangeABS'] = abs(t.myFundsChange)
            summary_dict['FinalDecision'] = h.histDecision
            summary_dict['FinalEquity'] = h.histEquity
            summary_dict['Template'] = t.current_strategy
            summary_dict['software_version'] = t.version
            summary_dict['ip'] = t.ip

            if abs(t.myFundsChange) <= float(p.selected_strategy['max_abs_fundchange']):
                t_write_db = threading.Thread(name='write_mongo', target=self._write_game_log, args=[summary_dict])
                t_write_db.daemon = True
                t_write_db.start()

    def _write_round_log(self, rec):
        _ensure_log_dir()
        filepath = os.path.join(LOG_DIR, f"rounds_{datetime.date.today()}.jsonl")
        try:
            with open(filepath, 'a', encoding='utf-8') as f:
                f.write(json.dumps(rec, default=str) + '\n')
        except Exception as e:
            log.error(f"Failed to write round log: {e}")

    def _write_game_log(self, rec):
        _ensure_log_dir()
        filepath = os.path.join(LOG_DIR, f"games_{datetime.date.today()}.jsonl")
        try:
            # Convert non-serializable types before writing
            safe_rec = {}
            for k, v in rec.items():
                try:
                    json.dumps(v, default=str)
                    safe_rec[k] = v
                except (TypeError, ValueError):
                    safe_rec[k] = str(v)
            with open(filepath, 'a', encoding='utf-8') as f:
                f.write(json.dumps(safe_rec, default=str) + '\n')
        except Exception as e:
            log.error(f"Failed to write game log: {e}")

    def insert_collusion(self, rec):
        _ensure_log_dir()
        filepath = os.path.join(LOG_DIR, f"collusion_{datetime.date.today()}.jsonl")
        try:
            with open(filepath, 'a', encoding='utf-8') as f:
                f.write(json.dumps(rec, default=str) + '\n')
        except Exception as e:
            log.error(f"Failed to write collusion log: {e}")

    def upload_collusion_data(self, gamenumber, mycards, p, gamestage):
        package = {'gamenumber': gamenumber, 'cards': str(mycards), 'computername': COMPUTER_NAME,
                   'strategy': p.current_strategy, 'timestamp': str(datetime.datetime.utcnow()), 'gamestage': gamestage}
        t_write_db = threading.Thread(
            name='write_collusion', target=self.insert_collusion, args=[package])
        t_write_db.daemon = True
        t_write_db.start()

    def get_collusion_cards(self, gamenumber, gamestage):
        return '', False

    def _load_local_games(self, strategy=None):
        _ensure_log_dir()
        all_records = []
        for fname in sorted(os.listdir(LOG_DIR)):
            if not fname.startswith('games_') or not fname.endswith('.jsonl'):
                continue
            filepath = os.path.join(LOG_DIR, fname)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if not line:
                            continue
                        try:
                            rec = json.loads(line)
                            if strategy is None or rec.get('Template') == strategy:
                                all_records.append(rec)
                        except json.JSONDecodeError:
                            continue
            except Exception:
                continue
        return all_records

    def _load_local_rounds(self):
        _ensure_log_dir()
        all_records = []
        for fname in sorted(os.listdir(LOG_DIR)):
            if not fname.startswith('rounds_') or not fname.endswith('.jsonl'):
                continue
            filepath = os.path.join(LOG_DIR, fname)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if not line:
                            continue
                        try:
                            all_records.append(json.loads(line))
                        except json.JSONDecodeError:
                            continue
            except Exception:
                continue
        return all_records

    def get_stacked_bar_data(self, p_name, p_value, chartType, last_stage='All', last_action='All'):
        records = self._load_local_games()
        if not records:
            return None
        return records

    def get_stacked_bar_data2(self, p_name, p_value, chartType, last_stage='All', last_action='All',
                              my_computer_only=False):
        records = self._load_local_games()
        if not records:
            return pd.DataFrame()
        return pd.DataFrame(records)

    def get_histrogram_data(self, p_name, p_value, game_stage, decision, my_computer_only=False):
        return [0, 0]

    def get_game_count(self, strategy, my_computer_only=False):
        records = self._load_local_games(strategy=strategy)
        return len(records)

    def get_strategy_return(self, strategy, days, my_computer_only=False):
        records = self._load_local_games(strategy=strategy)
        if not records:
            return 0.0
        total = sum(float(r.get('FinalFundsChange', 0)) for r in records)
        return round(total, 2)

    def get_fundschange_chart(self, strategy, my_computer_only=False):
        records = self._load_local_games(strategy=strategy)
        if not records:
            return []
        return [float(r.get('FinalFundsChange', 0)) for r in records]

    def get_scatterplot_data(self, p_name, p_value, game_stage, decision):
        return [pd.DataFrame(), pd.DataFrame()]

    def get_worst_games(self, strategy):
        records = self._load_local_games(strategy=strategy)
        if not records:
            return pd.DataFrame()
        return pd.DataFrame(records)