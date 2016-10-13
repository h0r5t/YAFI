import sys
sys.path.append('/finsymbols')
import finsymbols

def loadSP500Symbols():
    return finsymbols.get_sp500_symbols()
