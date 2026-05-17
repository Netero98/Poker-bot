import unittest
from unittest.mock import MagicMock
import numpy as np
from poker.decisionmaker.decisionmaker import Decision, DecisionTypes, GameStages

class TestDecisionMakerAbstract(unittest.TestCase):
    def setUp(self):
        self.strategy = MagicMock()
        # Default strategy parameters based on UI defaults
        self.strategy.selected_strategy = {
            'bigBlind': 0.02,
            'smallBlind': 0.01,
            'initialFunds': 2.0,
            'initialFunds2': 2.0,
            'use_pot_multiples': 0,
            'use_relative_equity': 0,
            'out_multiplier': 0,
            'pre_flop_equity_reduction_by_position': 0.01,
            'pre_flop_equity_increase_if_bet': 0.05,
            'pre_flop_equity_increase_if_call': 0.05,
            'potAdjustmentPreFlop': 1,
            'maxPotAdjustmentPreFlop': 1,
            'potAdjustment': 1,
            'maxPotAdjustment': 1,
            
            # PreFlop
            'PreFlopCallPower': 30,
            'PreFlopMinCallEquity': 0.45,
            'PreFlopBetPower': 30,
            'PreFlopMinBetEquity': 0.60,
            'PreFlopMaxBetEquity': 1.0,
            
            # Flop
            'FlopCallPower': 25,
            'FlopMinCallEquity': 0.40,
            'FlopBetPower': 25,
            'FlopMinBetEquity': 0.55,
            'FlopBluffMinEquity': 0.1,
            'FlopBluffMaxEquity': 0.3,
            
            # Turn
            'TurnCallPower': 20,
            'TurnMinCallEquity': 0.35,
            'TurnBetPower': 20,
            'TurnMinBetEquity': 0.50,
            'TurnBluffMinEquity': 0.1,
            'TurnBluffMaxEquity': 0.3,

            # River
            'RiverCallPower': 15,
            'RiverMinCallEquity': 0.30,
            'RiverBetPower': 15,
            'RiverMinBetEquity': 0.45,
            'RiverBluffMinEquity': 0.1,
            'RiverBluffMaxEquity': 0.3,
            
            'secondRoundAdjustmentPreFlop': 0.05,
            'secondRoundAdjustment': 0.05,
            'secondRoundAdjustmentPowerIncrease': 2,
            'alwaysCallEquity': 0.95,
            'always_call_low_stack_multiplier': 5,
            'preflop_override': 0, # Disable table lookup
            'secondRiverBetPotMinEquity': 0.8,
            'betPotRiverEquity': 0.8,
            'betPotRiverEquityMaxBBM': 50,
            'minimum_bet_size': 2,
            
            # Deception
            'FlopCheckDeceptionMinEquity': 0.95,
            'TurnCheckDeceptionMinEquity': 0.95,
            'RiverCheckDeceptionMinEquity': 0.95,
            
            # Conditions
            'flop_bluffing_condidion_1': 0,
            'turn_bluffing_condidion_1': 0,
            'turn_bluffing_condidion_2': 0,
            'river_bluffing_condidion_1': 0,
            'river_bluffing_condidion_2': 0,
            
            'opponent_raised_without_initiative_flop': 0,
            'opponent_raised_without_initiative_turn': 0,
            'opponent_raised_without_initiative_river': 0,
            
            'flop_betting_condidion_1': 0,
            'turn_betting_condidion_1': 0,
            'river_betting_condidion_1': 0,
            
            'BetPlusInc': 1,
            'minBullyEquity': 0.4,
            'maxBullyEquity': 0.6,
            'bullyDivider': 2,
            'c': 1.0, # used in calc_bet_limit? (actually not used in decisionmaker.py mostly, but good to have)
        }
        
        self.logger = MagicMock()
        self.history = MagicMock()
        self.history.histGameStage = ''
        self.history.lastRoundGameID = 0
        self.history.GameID = 1
        self.history.lastSecondRoundAdjustment = 0
        self.history.round_number = 0
        self.history.previous_decision = ''
        self.history.last_round_bluff = False
        self.history.myLastBet = 0
        self.history.preflop_sheet = {} 

        self.table = MagicMock()
        # Common table setup
        self.table.checkButton = False
        self.table.allInCallButton = False
        self.table.other_player_has_initiative = False
        self.table.first_raiser_utg = np.nan
        self.table.first_caller_utg = np.nan
        self.table.mycards = ['Ah', 'Kh'] # Dummy cards
        self.table.cardsOnTable = []
        self.table.position_utg_plus = 0
        self.table.totalPotValue = 0.5
        self.table.round_pot_value = 0.1
        self.table.minCall = 0.02
        self.table.minBet = 0.04
        self.table.myFunds = 2.0
        self.table.gameStage = GameStages.PreFlop.value
        self.table.isHeadsUp = True
        self.table.playersAhead = 0
        self.table.other_players = [{'pot': 0.02}] * 5
        self.table.max_X = 1
        self.table.relative_equity = 0.5
        self.table.range_equity = 0.5
        self.table.abs_equity = 0.5
        self.table.equity = 0.5 # Current equity
        self.table.PlayerNames = ['Bot', 'Opponent']

    def test_preflop_fold_low_equity(self):
        """Test forcing a fold preflop due to low equity."""
        self.table.equity = 0.2
        self.table.minCall = 0.1 # High call amount relative to equity
        
        decision_maker = Decision(self.table, self.history, self.strategy, self.logger)
        decision_maker.make_decision(self.table, self.history, self.strategy, self.logger)
        
        # Should fold because equity 0.2 is way below minCallEquity requirements for calling a 0.1 bet
        self.assertEqual(decision_maker.decision, DecisionTypes.fold.value)

    def test_preflop_call_good_equity(self):
        """Test calling/raising preflop with good equity."""
        self.table.equity = 0.65
        self.table.minCall = 0.02 # Small call
        self.table.checkButton = False
        
        decision_maker = Decision(self.table, self.history, self.strategy, self.logger)
        decision_maker.make_decision(self.table, self.history, self.strategy, self.logger)
        
        # Equity 0.65 is likely above MinBetEquity (0.60), so it might bet.
        # Or at least call.
        self.assertIn(decision_maker.decision, [DecisionTypes.call.value, DecisionTypes.bet1.value, DecisionTypes.bet2.value, DecisionTypes.bet3.value, DecisionTypes.bet4.value])

    def test_flop_check_deception(self):
        """Test check deception on Flop: high equity, checking to opponent."""
        self.table.gameStage = GameStages.Flop.value
        self.table.cardsOnTable = ['Ah', 'Ks', '2d']
        self.table.equity = 0.98 # Very high equity, nut hand
        self.table.checkButton = True
        self.table.minCall = 0.0
        self.strategy.selected_strategy['FlopCheckDeceptionMinEquity'] = 0.90
        
        # Normally high equity would trigger a bet
        decision_maker = Decision(self.table, self.history, self.strategy, self.logger)
        decision_maker.make_decision(self.table, self.history, self.strategy, self.logger)
        
        # Should be check deception
        self.assertEqual(decision_maker.decision, DecisionTypes.check_deception.value)

    def test_flop_bet_strong_hand(self):
        """Test betting for value on Flop."""
        self.table.gameStage = GameStages.Flop.value
        self.table.cardsOnTable = ['Ah', 'Ks', '2d']
        self.table.equity = 0.8
        self.table.checkButton = True
        self.table.minCall = 0.0
        self.table.minBet = 0.1
        self.strategy.selected_strategy['FlopCheckDeceptionMinEquity'] = 0.95 # Higher than our equity
        
        decision_maker = Decision(self.table, self.history, self.strategy, self.logger)
        decision_maker.make_decision(self.table, self.history, self.strategy, self.logger)
        
        # Should bet
        self.assertIn(decision_maker.decision, [DecisionTypes.bet1.value, DecisionTypes.bet2.value, DecisionTypes.bet3.value, DecisionTypes.bet4.value])

    def test_turn_bluff(self):
        """Test bluffing on Turn when equity is low but conditions allowed."""
        self.table.gameStage = GameStages.Turn.value
        self.table.cardsOnTable = ['Ah', 'Ks', '2d', '4c']
        self.table.equity = 0.15 # Low equity
        
        # Bluff conditions
        self.strategy.selected_strategy['TurnBluffMinEquity'] = 0.10
        self.strategy.selected_strategy['TurnBluffMaxEquity'] = 0.20
        self.strategy.selected_strategy['turn_bluffing_condidion_1'] = 0 # No condition
        self.strategy.selected_strategy['turn_bluffing_condidion_2'] = 0 
        
        self.table.checkButton = True # We can check, so we initiated action (or checked to us)
        self.table.playersAhead = 0
        self.table.other_player_has_initiative = False
        
        decision_maker = Decision(self.table, self.history, self.strategy, self.logger)
        # Force initial decision to likely be check (due to low equity)
        # The bluff logic runs AFTER regular logic and overrides it if conditions met.
        decision_maker.make_decision(self.table, self.history, self.strategy, self.logger)
        
        self.assertEqual(decision_maker.decision, DecisionTypes.bet_bluff.value)

    def test_river_fold_to_bet(self):
        """Test folding on River facing a bet with mediocre equity."""
        self.table.gameStage = GameStages.River.value
        self.table.cardsOnTable = ['Ah', 'Ks', '2d', '4c', '9s']
        self.table.equity = 0.2
        self.table.minCall = 1.0 # Large bet
        self.table.totalPotValue = 2.0
        self.table.checkButton = False
        
        decision_maker = Decision(self.table, self.history, self.strategy, self.logger)
        decision_maker.make_decision(self.table, self.history, self.strategy, self.logger)
        
        self.assertEqual(decision_maker.decision, DecisionTypes.fold.value)

    def test_river_check_behind(self):
        """Test checking behind on River with weak/medium hand."""
        self.table.gameStage = GameStages.River.value
        self.table.cardsOnTable = ['Ah', 'Ks', '2d', '4c', '9s']
        self.table.equity = 0.5
        self.table.checkButton = True
        self.table.minCall = 0.0
        
        # Set high min bet equity so we don't bet
        self.strategy.selected_strategy['RiverMinBetEquity'] = 0.6
        self.strategy.selected_strategy['RiverBluffMaxEquity'] = 0.4 # Don't bluff
        
        decision_maker = Decision(self.table, self.history, self.strategy, self.logger)
        decision_maker.make_decision(self.table, self.history, self.strategy, self.logger)
        
        # Should check (which maps to check or check_deception or just check if checkButton is True)
        # DecisionMaker usually returns 'Check' if decision is check or fold but check button exists.
        self.assertIn(decision_maker.decision, [DecisionTypes.check.value, DecisionTypes.check_deception.value])

    def test_pot_adjustment(self):
        """Test that pot adjustment logic affects call limit."""
        self.table.equity = 0.6
        self.table.gameStage = GameStages.Flop.value
        self.table.minCall = 0.05
        
        # Base case
        self.strategy.selected_strategy['potAdjustment'] = 0
        d1 = Decision(self.table, self.history, self.strategy, self.logger)
        limit1 = d1.finalCallLimit
        
        # With adjustment
        self.strategy.selected_strategy['potAdjustment'] = 2 # High adjustment
        self.table.totalPotValue = 1.0 # Ensure meaningful pot size
        d2 = Decision(self.table, self.history, self.strategy, self.logger)
        limit2 = d2.finalCallLimit
        
        # Decisionmaker subtracts potAdjustment from minCallEquity target, effectively making it easier to call?
        # Re-reading code: 
        # t.minEquityCall = ... - self.potAdjustment ...
        # If minEquityCall is lower, the curve fitting should yield a higher call limit for the same equity.
        # Or same limit for lower equity.
        # Here we have fixed equity.
        # d = Curvefitting(... minEquityCall ...)
        # If minEquityCall decreases, the curve shifts left/up (easier to call).
        
        # Actually comparing limits might be tricky due to curve fitting complexity.
        # But we expect some difference.
        self.assertNotEqual(limit1, limit2)

if __name__ == '__main__':
    unittest.main()
