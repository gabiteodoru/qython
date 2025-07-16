"""
Qython: Python-like syntax with q-functional constructs translator

Qython is a Python-like syntax that compiles to q/kdb+ code, featuring:
- Python-like control flow (if/else, for loops, function definitions)
- Q-functional constructs (converge, partial application, arange)
- Seamless integration with q/kdb+ systems

Example:
    from qython import translate_qython_to_q
    
    qython_code = '''
    def compound_growth(principal, rate, years):
        amount = principal
        do years times:
            amount = amount * (1 + rate)
        return amount
    '''
    
    q_code = translate_qython_to_q(qython_code)
"""

from .translate import translate_qython_to_q

__version__ = "0.1.0"
__author__ = "Gabi Teodoru"
__email__ = "gabiteodoru@gmail.com"

__all__ = ["translate_qython_to_q"]