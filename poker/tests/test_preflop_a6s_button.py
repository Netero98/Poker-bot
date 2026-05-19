"""
Test for preflop decision: A6s on Button vs UTG raise
Screenshot: Screenshot from Screen Recording 2026-05-17 213935.mp4 - 1.png

Situation:
- Game: NL2 Rush & Cash (Natural8/GGPoker)
- Hero: DanVoFloPopadan with A♣6♣ suited on Button
- Stack: 102 BB
- Action: UTG (sdvGGenius) raised to 3 BB
- All other players folded
- Expected decision: Call (based on 6R1 preflop sheet)

From preflop sheet 6R1 (Button vs UTG raise):
- A6s: Call=0.94, Raise=0.06, Fold=0.00
- With random < 0.94, decision should be Call
"""
import os
import unittest
from unittest.mock import MagicMock, patch

import numpy as np
import pandas as pd

from poker.decisionmaker.decisionmaker import Decision, DecisionTypes
from poker.tests import PREFLOP_PATH
from poker.tools.strategy_handler import StrategyHandler
from poker.decisionmaker.current_hand_memory import History
from poker.decisionmaker.montecarlo_python import MonteCarlo


class MockTable:
    """Mock table object for testing preflop decisions without image recognition"""
    
    def __init__(self):
        # Game state
        self.gameStage = "PreFlop"
        self.isHeadsUp = False
        self.checkButton = False
        self.allInCallButton = False
        self.position_utg_plus = 5  # Button is UTG+5
        
        # Raiser/caller info
        self.first_raiser_utg = 0  # UTG raised
        self.first_raiser = 2
        self.second_raiser_utg = np.nan
        self.first_caller_utg = np.nan
        self.second_raiser = np.nan
        
        # Pot and bet info
        self.currentCallValue = 0.04  # $0.04 = 2 BB to call
        self.currentBetValue = 0.10  # $0.10 = 5 BB
        self.minCall = 0.04
        self.minBet = 0.10
        self.totalPotValue = 0.045  # 4.5 BB
        self.bigBlind = 0.02
        self.smallBlind = 0.01
        self.round_pot_value = 0.06
        
        # Cards
        self.mycards = ['AC', '6C']  # A♣6♣
        
        # Other table properties
        self.other_player_has_initiative = False
        self.playersAhead = 1
        self.playersBehind = 0
        self.other_active_players = 1
        self.max_X = 0.95
        
        # Mock other_players structure
        self.other_players = [
            {'abs_position': 0, 'utg_position': 0, 'status': 1, 'pot': 0.06, 'funds': 1.63, 'name': 'sdvGGenius'},
            {'abs_position': 1, 'utg_position': 1, 'status': 0, 'pot': '', 'funds': '', 'name': ''},
            {'abs_position': 2, 'utg_position': 2, 'status': 0, 'pot': '', 'funds': '', 'name': ''},
            {'abs_position': 3, 'utg_position': 3, 'status': 0, 'pot': '', 'funds': '', 'name': ''},
            {'abs_position': 4, 'utg_position': 4, 'status': 0, 'pot': 0.02, 'funds': 10.90, 'name': 'Zloivase'},
        ]
        
        self.dealer_position = 2  # Dealer at position 2 means we're on button
        self.big_blind_position_abs_all = 4
        self.big_blind_position_abs_op = 3
        
        # Player info
        self.PlayerNames = ['sdvGGenius']
        self.total_players = 6
        self.myFunds = 2.04  # 102 BB at NL2
        
        # Cards on table
        self.cardsOnTable = []  # PreFlop
        self.abs_equity = 0.45  # Approximate equity for A6s
        self.equity = self.abs_equity
        
        # For derive_preflop_sheet_name
        self.preflop_sheet_name = ''
        
    def derive_preflop_sheet_name(self, t, h, first_raiser_utg, first_caller_utg, second_raiser_utg):
        """Generate preflop sheet name based on position and action"""
        first_raiser_string = 'R' if not np.isnan(first_raiser_utg) else ''
        first_raiser_number = str(int(first_raiser_utg) + 1) if first_raiser_string != '' else ''
        
        second_raiser_string = 'R' if not np.isnan(second_raiser_utg) else ''
        second_raiser_number = str(int(second_raiser_utg) + 1) if second_raiser_string != '' else ''
        
        first_caller_string = 'C' if not np.isnan(first_caller_utg) else ''
        first_caller_number = str(int(first_caller_utg) + 1) if first_caller_string != '' else ''
        
        round_string = '2' if h.round_number == 1 else ''
        
        sheet_name = str(t.position_utg_plus + 1) + \
                     round_string + \
                     str(first_raiser_string) + str(first_raiser_number) + \
                     str(second_raiser_string) + str(second_raiser_number) + \
                     str(first_caller_string) + str(first_caller_number)
        
        if h.round_number == 2:
            sheet_name = 'R1R2R1A2'
        
        self.preflop_sheet_name = sheet_name
        return sheet_name


class TestPreflopA6sButtonVsUtgRaise(unittest.TestCase):
    """Test that A6s on Button calls vs UTG raise"""

    def setUp(self):
        """Setup test fixtures"""
        self.strategy_name = 'Trial 1'
        
    def test_a6s_button_vs_utg_raise_calls(self):
        """
        Test scenario:
        - Hero on Button with A6s
        - UTG raises to 3 BB
        - All others fold
        - Expected: Call (based on 6R1 preflop sheet)
        """
        # Create mock table
        table = MockTable()
        
        # Setup strategy with preflop override enabled
        strategy = StrategyHandler()
        strategy.read_strategy(self.strategy_name)
        strategy.selected_strategy['preflop_override'] = '1'  # Enable preflop table
        
        # Setup history
        history = History()
        history.preflop_sheet = pd.read_excel(PREFLOP_PATH, sheet_name=None, engine='openpyxl')
        history.round_number = 0
        history.GameID = 12345
        history.lastRoundGameID = 12345
        history.histGameStage = ''
        history.myLastBet = 0
        history.previous_decision = None
        history.lastSecondRoundAdjustment = 0
        
        logger = MagicMock()
        
        # Create decision maker
        d = Decision(table, history, strategy, logger)
        
        # Analyze preflop table
        d.preflop_table_analyser(table, history, strategy)
        
        # Verify the correct preflop sheet is being used
        self.assertEqual(table.preflop_sheet_name, '6R1')
        
        # Verify A6s is in the preflop ranges
        self.assertIn('A6S', d.preflop_bot_ranges)
        
        # Test with mocked random to force Call decision
        # A6s in 6R1 has Call=0.94, so random < 0.94 should result in Call
        with patch('random.random', return_value=0.5):  # 0.5 < 0.94, so should Call
            d2 = Decision(table, history, strategy, logger)
            d2.preflop_table_analyser(table, history, strategy)
            d2.make_decision(table, history, strategy, logger)
            
            self.assertEqual(d2.decision, DecisionTypes.call.value)
            print(f"\nDecision with random=0.5: {d2.decision}")

    def test_a6s_button_vs_utg_raise_sheet_verification(self):
        """
        Verify that the correct preflop sheet is selected for this scenario
        and that A6s has the expected probabilities.
        """
        # Load preflop sheet directly
        excel_file = pd.read_excel(PREFLOP_PATH, sheet_name=None, engine='openpyxl')
        
        # For Button vs UTG raise, sheet name is 6R1
        self.assertIn('6R1', excel_file.keys(), "Sheet 6R1 should exist")
        
        sheet = excel_file['6R1']
        sheet['Hand'] = sheet['Hand'].apply(lambda x: str(x).upper())
        
        # Find A6s in the sheet
        a6s_rows = sheet[sheet['Hand'] == 'A6S']
        self.assertEqual(len(a6s_rows), 1, "A6s should be in the 6R1 sheet")
        
        a6s_row = a6s_rows.iloc[0]
        
        # A6s should have high call probability and low fold probability
        self.assertAlmostEqual(a6s_row['Call'], 0.94, places=2, msg="A6s Call probability should be ~0.94")
        self.assertAlmostEqual(a6s_row['Raise'], 0.06, places=2, msg="A6s Raise probability should be ~0.06")
        self.assertAlmostEqual(a6s_row['Fold'], 0.00, places=2, msg="A6s Fold probability should be ~0.00")
        
        print(f"\nA6s probabilities in 6R1 sheet:")
        print(f"  Call: {a6s_row['Call']}")
        print(f"  Raise: {a6s_row['Raise']}")
        print(f"  Fold: {a6s_row['Fold']}")

    def test_preflop_decision_with_different_random_values(self):
        """
        Test that the decision changes based on random value as expected.
        A6s in 6R1: Call=0.94, Raise=0.06
        - random < 0.94: Call
        - 0.94 <= random < 1.00: Raise
        """
        table = MockTable()
        
        strategy = StrategyHandler()
        strategy.read_strategy(self.strategy_name)
        strategy.selected_strategy['preflop_override'] = '1'
        
        history = History()
        history.preflop_sheet = pd.read_excel(PREFLOP_PATH, sheet_name=None, engine='openpyxl')
        history.round_number = 0
        history.GameID = 12345
        history.lastRoundGameID = 12345
        history.histGameStage = ''
        history.myLastBet = 0
        history.previous_decision = None
        history.lastSecondRoundAdjustment = 0
        
        logger = MagicMock()
        
        # Test with random = 0.1 (should Call)
        with patch('random.random', return_value=0.1):
            d = Decision(table, history, strategy, logger)
            d.preflop_table_analyser(table, history, strategy)
            d.make_decision(table, history, strategy, logger)
            self.assertEqual(d.decision, DecisionTypes.call.value, 
                           "With random=0.1, should Call (0.1 < 0.94)")
        
        # Test with random = 0.95 (should Raise - above Call threshold but below Call+Raise)
        with patch('random.random', return_value=0.95):
            d = Decision(table, history, strategy, logger)
            d.preflop_table_analyser(table, history, strategy)
            d.make_decision(table, history, strategy, logger)
            # 0.95 >= 0.94 and 0.95 <= 0.94 + 0.06 = 1.0, so should Raise
            self.assertEqual(d.decision, DecisionTypes.bet4.value,
                           "With random=0.95, should Raise (0.95 >= 0.94)")

    def test_sheet_name_generation_button_utg(self):
        """
        Test that derive_preflop_sheet_name generates correct sheet name
        for Button vs UTG raise scenario.
        """
        table = MockTable()
        history = MagicMock()
        history.round_number = 0
        
        # Generate sheet name for Button vs UTG raise
        sheet_name = table.derive_preflop_sheet_name(
            table, history, 
            first_raiser_utg=0,      # UTG raised (position 0)
            first_caller_utg=np.nan,
            second_raiser_utg=np.nan
        )
        
        self.assertEqual(sheet_name, '6R1', 
                        "Button (position 6) vs UTG (position 1) raise should produce sheet '6R1'")

    def test_hand_notation_conversion(self):
        """
        Test that A6s is correctly converted to the format used in preflop sheets.
        """
        m = MonteCarlo()
        crd1, crd2 = m.get_two_short_notation(['AC', '6C'])  # A♣6♣
        
        print(f"\nCard notation conversion:")
        print(f"  Input: ['AC', '6C']")
        print(f"  Output: crd1='{crd1}', crd2='{crd2}'")
        
        # The cards should be converted to short notation
        self.assertIn(crd1.upper(), ['A6S', '6AS'])
        self.assertIn(crd2.upper(), ['A6S', '6AS'])


class TestPreflopEdgeCases(unittest.TestCase):
    """Test edge cases for preflop decisions"""
    
    def test_hand_not_in_preflop_sheet_folds(self):
        """
        Test that if the hand is not in the preflop sheet, the decision is Fold.
        Using a trash hand like 72o which should not be in 6R1 sheet.
        """
        table = MockTable()
        table.mycards = ['7C', '2H']  # 72o (trash hand)
        
        strategy = StrategyHandler()
        strategy.read_strategy('Trial 1')
        strategy.selected_strategy['preflop_override'] = '1'
        
        history = History()
        history.preflop_sheet = pd.read_excel(PREFLOP_PATH, sheet_name=None, engine='openpyxl')
        history.round_number = 0
        history.GameID = 12345
        history.lastRoundGameID = 12345
        history.histGameStage = ''
        history.myLastBet = 0
        history.previous_decision = None
        history.lastSecondRoundAdjustment = 0
        
        logger = MagicMock()
        
        d = Decision(table, history, strategy, logger)
        d.preflop_table_analyser(table, history, strategy)
        d.make_decision(table, history, strategy, logger)
        
        # Hand not in sheet should result in Fold
        self.assertEqual(d.decision, DecisionTypes.fold.value,
                        "Hand not in preflop sheet should result in Fold")
        print(f"\n72o decision (not in sheet): {d.decision}")

    def test_strong_hand_raises(self):
        """
        Test that a strong hand like AA raises instead of calls.
        AA in 6R1: Call=0.00, Raise=1.00
        """
        table = MockTable()
        table.mycards = ['AC', 'AD']  # AA
        
        strategy = StrategyHandler()
        strategy.read_strategy('Trial 1')
        strategy.selected_strategy['preflop_override'] = '1'
        
        history = History()
        history.preflop_sheet = pd.read_excel(PREFLOP_PATH, sheet_name=None, engine='openpyxl')
        history.round_number = 0
        history.GameID = 12345
        history.lastRoundGameID = 12345
        history.histGameStage = ''
        history.myLastBet = 0
        history.previous_decision = None
        history.lastSecondRoundAdjustment = 0
        
        logger = MagicMock()
        
        # With any random value, AA should raise (Raise probability = 1.00)
        with patch('random.random', return_value=0.5):
            d = Decision(table, history, strategy, logger)
            d.preflop_table_analyser(table, history, strategy)
            d.make_decision(table, history, strategy, logger)
            
            self.assertEqual(d.decision, DecisionTypes.bet4.value,
                           "AA should Raise with 100% probability")
            print(f"\nAA decision: {d.decision}")


class TestPreflopA6sScenarioDescription(unittest.TestCase):
    """Documentation test describing the scenario"""
    
    def test_scenario_description(self):
        """
        Document the exact scenario from the screenshot.
        """
        scenario = {
            'game': 'NL2 Rush & Cash (Natural8/GGPoker)',
            'hero_name': 'DanVoFloPopadan',
            'hero_position': 'Button',
            'hero_cards': 'A♣6♣ (A6s - suited)',
            'hero_stack': '102 BB',
            'action': 'UTG (sdvGGenius) raises to 3 BB',
            'pot': '4.5 BB',
            'other_players': [
                'olcham7: Fold (171.5 BB)',
                'elchaza3011: Fold (265 BB)',
                'Michi_Sad-U__U: Fold (101 BB)',
                'Zloivase: BB (545 BB)',
                'sdvGGenius: Raise 3 BB (81.5 BB)'
            ],
            'expected_sheet': '6R1',
            'expected_decision': 'Call (94% probability)'
        }
        
        print("\n" + "="*60)
        print("SCENARIO DESCRIPTION")
        print("="*60)
        for key, value in scenario.items():
            if isinstance(value, list):
                print(f"{key}:")
                for item in value:
                    print(f"  - {item}")
            else:
                print(f"{key}: {value}")
        print("="*60)
        
        # This test always passes, it's just for documentation
        self.assertTrue(True)


if __name__ == '__main__':
    unittest.main(verbosity=2)
