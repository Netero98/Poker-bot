import os

from PyQt6 import uic
from PyQt6.QtWidgets import QMainWindow, QDialog

_GUI_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ui')


class AnalyserForm(QMainWindow):

    def __init__(self):
        super(AnalyserForm, self).__init__()
        uic.loadUi(os.path.join(_GUI_DIR, 'analyser_form.ui'), self)

        self.show()


class TableSetupForm(QMainWindow):

    def __init__(self):
        super(TableSetupForm, self).__init__()
        uic.loadUi(os.path.join(_GUI_DIR, 'table_setup_form.ui'), self)

        self.show()


class SetupForm(QMainWindow):
    def __init__(self):
        super(SetupForm, self).__init__()
        uic.loadUi(os.path.join(_GUI_DIR, 'setup_form.ui'), self)

        self.show()


class StrategyEditorForm(QMainWindow):

    def __init__(self):
        super(StrategyEditorForm, self).__init__()
        uic.loadUi(os.path.join(_GUI_DIR, 'strategy_manager_form.ui'), self)

        self.show()


class GeneticAlgo(QDialog):

    def __init__(self):
        super(GeneticAlgo, self).__init__()
        uic.loadUi(os.path.join(_GUI_DIR, 'genetic_algo_form.ui'), self)
        self.show()


class MainForm(QMainWindow):

    def __init__(self):
        super(MainForm, self).__init__()
        uic.loadUi(os.path.join(_GUI_DIR, 'main_form.ui'), self)

        self.show()


class UiPokerbot(QMainWindow):

    def __init__(self):
        super(UiPokerbot, self).__init__()
        uic.loadUi(os.path.join(_GUI_DIR, 'main_form.ui'), self)

        self.show()
