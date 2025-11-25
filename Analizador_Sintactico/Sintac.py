class SyntaxAnalyzer:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.current = self.tokens[0] if tokens else None
        self.errors = []
    
    def advance(self):
        """Move to the next token"""
        self.pos += 1
        if self.pos < len(self.tokens):
            self.current = self.tokens[self.pos]
        else:
            self.current = None
    
    def match(self, expected):
        """Check if current token matches expected token"""
        if self.current == expected:
            self.advance()
            return True
        return False
    
    def error(self, expected):
        """Record syntax error"""
        msg = f"Error en posición {self.pos}: Se esperaba '{expected}', se encontró '{self.current}'"
        self.errors.append(msg)
        return False
    
    # ========== Main Program Structure ==========
    def Program(self):
        """Program -> Class Program'"""
        if not self.Class():
            return False
        return self.ProgramPrime()
    
    def ProgramPrime(self):
        """Program' -> Func Program' | ε"""
        if self.current and self.current == "FUNCTION":
            if not self.Func():
                return False
            return self.ProgramPrime()
        return True  # ε
    
    def Class(self):
        """Class -> process id delim_lkey Cont delim_rkey end_process"""
        if not self.match("PROCESS"):
            return self.error("PROCESS")
        if not self.match("ID"):
            return self.error("ID")
        if not self.match("DELIM_LKEY"):
            return self.error("DELIM_LKEY")
        if not self.Cont():
            return False
        if not self.match("DELIM_RKEY"):
            return self.error("DELIM_RKEY")
        if not self.match("END_PROCESS"):
            return self.error("END_PROCESS")
        return True
    
    def Cont(self):
        """Cont -> Accon Cont'"""
        if not self.Accon():
            return False
        return self.ContPrime()
    
    def ContPrime(self):
        """Cont' -> Accon Cont' | ε"""
        if self.current in ["DEFINIR", "ID", "WRITE", "READ", "IF", "FOR", "REPEAT", "WHILE", "SWITCH"]:
            if not self.Accon():
                return False
            return self.ContPrime()
        return True  # ε
    
    def Accon(self):
        """Accon -> Defi | Asig | Impr | Lect | Condif | CycleFor | CycleRep | CycleWhile | Multselec"""
        if self.current == "DEFINIR":
            return self.Defi()
        elif self.current == "ID":
            return self.Asig()
        elif self.current == "WRITE":
            return self.Impr()
        elif self.current == "READ":
            return self.Lect()
        elif self.current == "IF":
            return self.Condif()
        elif self.current == "FOR":
            return self.CycleFor()
        elif self.current == "REPEAT":
            return self.CycleRep()
        elif self.current == "WHILE":
            return self.CycleWhile()
        elif self.current == "SWITCH":
            return self.Multselec()
        else:
            return self.error("DEFINIR, ID, WRITE, READ, IF, FOR, REPEAT, WHILE, or SWITCH")
    
    # ========== Conditional Structure ==========
    def Condif(self):
        """Condif -> if delim_lparen Exprelog delim_rparen then delim_lkey Cont delim_rkey Condif'"""
        if not self.match("IF"):
            return self.error("IF")
        if not self.match("DELIM_LPAREN"):
            return self.error("DELIM_LPAREN")
        if not self.Exprelog():
            return False
        if not self.match("DELIM_RPAREN"):
            return self.error("DELIM_RPAREN")
        if not self.match("THEN"):
            return self.error("THEN")
        if not self.match("DELIM_LKEY"):
            return self.error("DELIM_LKEY")
        if not self.Cont():
            return False
        if not self.match("DELIM_RKEY"):
            return self.error("DELIM_RKEY")
        return self.CondifPrime()
    
    def CondifPrime(self):
        """Condif' -> else delim_lkey Cont delim_rkey end_if | end_if"""
        if self.current == "ELSE":
            self.advance()
            if not self.match("DELIM_LKEY"):
                return self.error("DELIM_LKEY")
            if not self.Cont():
                return False
            if not self.match("DELIM_RKEY"):
                return self.error("DELIM_RKEY")
            if not self.match("END_IF"):
                return self.error("END_IF")
            return True
        elif self.current == "END_IF":
            self.advance()
            return True
        else:
            return self.error("ELSE or END_IF")
    
    # ========== Function ==========
    def Func(self):
        """Func -> function id equal id delim_lparen Varmul delim_rparen delim_lkey Cont delim_rkey end_function"""
        if not self.match("FUNCTION"):
            return self.error("FUNCTION")
        if not self.match("ID"):
            return self.error("ID")
        if not self.match("EQUAL"):
            return self.error("EQUAL")
        if not self.match("ID"):
            return self.error("ID")
        if not self.match("DELIM_LPAREN"):
            return self.error("DELIM_LPAREN")
        if not self.Varmul():
            return False
        if not self.match("DELIM_RPAREN"):
            return self.error("DELIM_RPAREN")
        if not self.match("DELIM_LKEY"):
            return self.error("DELIM_LKEY")
        if not self.Cont():
            return False
        if not self.match("DELIM_RKEY"):
            return self.error("DELIM_RKEY")
        if not self.match("END_FUNCTION"):
            return self.error("END_FUNCTION")
        return True
    
    # ========== Cycles ==========
    def CycleWhile(self):
        """CycleWhile -> while delim_lparen Exprelog delim_rparen do delim_lkey Contblo delim_rkey end_while"""
        if not self.match("WHILE"):
            return self.error("WHILE")
        if not self.match("DELIM_LPAREN"):
            return self.error("DELIM_LPAREN")
        if not self.Exprelog():
            return False
        if not self.match("DELIM_RPAREN"):
            return self.error("DELIM_RPAREN")
        if not self.match("DO"):
            return self.error("DO")
        if not self.match("DELIM_LKEY"):
            return self.error("DELIM_LKEY")
        if not self.Contblo():
            return False
        if not self.match("DELIM_RKEY"):
            return self.error("DELIM_RKEY")
        if not self.match("END_WHILE"):
            return self.error("END_WHILE")
        return True
    
    def CycleRep(self):
        """CycleRep -> repeat delim_lkey Contblo delim_rkey until delim_lparen Exprelog delim_rparen"""
        if not self.match("REPEAT"):
            return self.error("REPEAT")
        if not self.match("DELIM_LKEY"):
            return self.error("DELIM_LKEY")
        if not self.Contblo():
            return False
        if not self.match("DELIM_RKEY"):
            return self.error("DELIM_RKEY")
        if not self.match("UNTIL"):
            return self.error("UNTIL")
        if not self.match("DELIM_LPAREN"):
            return self.error("DELIM_LPAREN")
        if not self.Exprelog():
            return False
        if not self.match("DELIM_RPAREN"):
            return self.error("DELIM_RPAREN")
        return True
    
    def CycleFor(self):
        """CycleFor -> for id equal data_int through data_int rate data_int do_for delim_lkey Contblo delim_rkey end_for"""
        if not self.match("FOR"):
            return self.error("FOR")
        if not self.match("ID"):
            return self.error("ID")
        if not self.match("EQUAL"):
            return self.error("EQUAL")
        if not self.match("DATA_INT"):
            return self.error("DATA_INT")
        if not self.match("THROUGH"):
            return self.error("THROUGH")
        if not self.match("DATA_INT"):
            return self.error("DATA_INT")
        if not self.match("RATE"):
            return self.error("RATE")
        if not self.match("DATA_INT"):
            return self.error("DATA_INT")
        if not self.match("DO_FOR"):
            return self.error("DO_FOR")
        if not self.match("DELIM_LKEY"):
            return self.error("DELIM_LKEY")
        if not self.Contblo():
            return False
        if not self.match("DELIM_RKEY"):
            return self.error("DELIM_RKEY")
        if not self.match("END_FOR"):
            return self.error("END_FOR")
        return True
    
    # ========== Multi-Selection (Switch) ==========
    def Multselec(self):
        """Multselec -> switch delim_lparen id delim_rparen select Multselec' default delim_enter delim_lkey Contswi delim_rkey"""
        if not self.match("SWITCH"):
            return self.error("SWITCH")
        if not self.match("DELIM_LPAREN"):
            return self.error("DELIM_LPAREN")
        if not self.match("ID"):
            return self.error("ID")
        if not self.match("DELIM_RPAREN"):
            return self.error("DELIM_RPAREN")
        if not self.match("SELECT"):
            return self.error("SELECT")
        if not self.MultselecPrime():
            return False
        if not self.match("DEFAULT"):
            return self.error("DEFAULT")
        if not self.match("DELIM_ENTER"):
            return self.error("DELIM_ENTER")
        if not self.match("DELIM_LKEY"):
            return self.error("DELIM_LKEY")
        if not self.Contswi():
            return False
        if not self.match("DELIM_RKEY"):
            return self.error("DELIM_RKEY")
        return True
    
    def MultselecPrime(self):
        """Multselec' -> Multselec'' Multselec' | ε"""
        if self.current == "DATA_INT":
            if not self.MultselecDoublePrime():
                return False
            return self.MultselecPrime()
        return True  # ε
    
    def MultselecDoublePrime(self):
        """Multselec'' -> data_int delim_enter delim_lkey Contswi delim_rkey"""
        if not self.match("DATA_INT"):
            return self.error("DATA_INT")
        if not self.match("DELIM_ENTER"):
            return self.error("DELIM_ENTER")
        if not self.match("DELIM_LKEY"):
            return self.error("DELIM_LKEY")
        if not self.Contswi():
            return False
        if not self.match("DELIM_RKEY"):
            return self.error("DELIM_RKEY")
        return True
    
    # ========== Block Content ==========
    def Contblo(self):
        """Contblo -> Acblo Contblo'"""
        if not self.Acblo():
            return False
        return self.ContbloPrime()
    
    def ContbloPrime(self):
        """Contblo' -> Acblo Contblo' | ε"""
        if self.current in ["ID", "WRITE", "READ", "IF", "FOR", "REPEAT", "WHILE", "SWITCH"]:
            if not self.Acblo():
                return False
            return self.ContbloPrime()
        return True  # ε
    
    def Acblo(self):
        """Acblo -> Asig | Impr | Lect | Condif | CycleFor | CycleRep | CycleWhile | Multselec"""
        if self.current == "ID":
            return self.Asig()
        elif self.current == "WRITE":
            return self.Impr()
        elif self.current == "READ":
            return self.Lect()
        elif self.current == "IF":
            return self.Condif()
        elif self.current == "FOR":
            return self.CycleFor()
        elif self.current == "REPEAT":
            return self.CycleRep()
        elif self.current == "WHILE":
            return self.CycleWhile()
        elif self.current == "SWITCH":
            return self.Multselec()
        else:
            return self.error("ID, WRITE, READ, IF, FOR, REPEAT, WHILE, or SWITCH")
    
    # ========== Switch Content ==========
    def Contswi(self):
        """Contswi -> Acswi Contswi'"""
        if not self.Acswi():
            return False
        return self.ContswiPrime()
    
    def ContswiPrime(self):
        """Contswi' -> Acswi Contswi' | ε"""
        if self.current in ["ID", "WRITE", "READ", "IF", "FOR", "REPEAT", "WHILE"]:
            if not self.Acswi():
                return False
            return self.ContswiPrime()
        return True  # ε
    
    def Acswi(self):
        """Acswi -> Asig | Impr | Lect | Condif | CycleFor | CycleRep | CycleWhile"""
        if self.current == "ID":
            return self.Asig()
        elif self.current == "WRITE":
            return self.Impr()
        elif self.current == "READ":
            return self.Lect()
        elif self.current == "IF":
            return self.Condif()
        elif self.current == "FOR":
            return self.CycleFor()
        elif self.current == "REPEAT":
            return self.CycleRep()
        elif self.current == "WHILE":
            return self.CycleWhile()
        else:
            return self.error("ID, WRITE, READ, IF, FOR, REPEAT, or WHILE")
    
    # ========== Logical Expressions ==========
    def Exprelog(self):
        """Exprelog -> Log Exprelog'"""
        if not self.Log():
            return False
        return self.ExprelogPrime()
    
    def ExprelogPrime(self):
        """Exprelog' -> Opelog Log Exprelog' | ε"""
        if self.current in ["AND", "OR", "NOT"]:
            if not self.Opelog():
                return False
            if not self.Log():
                return False
            return self.ExprelogPrime()
        return True  # ε
    
    def Log(self):
        """Log -> id Opeasig Valorlog | Valornum Opeasig Valorlog"""
        if self.current == "ID":
            self.advance()
            if not self.Opeasig():
                return False
            return self.Valorlog()
        elif self.current in ["DATA_INT", "DATA_DOUBLE"]:
            if not self.Valornum():
                return False
            if not self.Opeasig():
                return False
            return self.Valorlog()
        else:
            return self.error("ID, DATA_INT, or DATA_DOUBLE")
    
    # ========== Math Expressions ==========
    def Expremath(self):
        """Expremath -> Valornum Expremath' | Mathfunc"""
        if self.current in ["DATA_INT", "DATA_DOUBLE"]:
            if not self.Valornum():
                return False
            return self.ExpremathPrime()
        elif self.current in ["FUN_SQRT", "FUN_ABS", "FUN_LN", "FUN_EXP", "FUN_SEN", "FUN_COS", "FUN_ATAN", "FUN_TRUNC", "FUN_ROUND", "FUN_RAND"]:
            return self.Mathfunc()
        else:
            return self.error("DATA_INT, DATA_DOUBLE, or Math Function")
    
    def ExpremathPrime(self):
        """Expremath' -> Simb Valorlog | ε"""
        if self.current in ["PLUS", "MINUS", "MULT", "DIV", "EXP", "MODULO"]:
            if not self.Simb():
                return False
            return self.Valorlog()
        return True  # ε
    
    def Mathfunc(self):
        """Mathfunc -> Mathfunc' delim_lparen id delim_rparen"""
        if not self.MathfuncPrime():
            return False
        if not self.match("DELIM_LPAREN"):
            return self.error("DELIM_LPAREN")
        if not self.match("ID"):
            return self.error("ID")
        if not self.match("DELIM_RPAREN"):
            return self.error("DELIM_RPAREN")
        return True
    
    def MathfuncPrime(self):
        """Mathfunc' -> fun_sqrt | fun_abs | fun_ln | fun_exp | fun_sen | fun_cos | fun_atan | fun_trunc | fun_round | fun_rand"""
        if self.current in ["FUN_SQRT", "FUN_ABS", "FUN_LN", "FUN_EXP", "FUN_SEN", "FUN_COS", "FUN_ATAN", "FUN_TRUNC", "FUN_ROUND", "FUN_RAND"]:
            self.advance()
            return True
        return self.error("Math Function")
    
    # ========== String Expressions ==========
    def Exprestring(self):
        """Exprestring -> data_string Exprestring'"""
        if not self.match("DATA_STRING"):
            return self.error("DATA_STRING")
        return self.ExprestringPrime()
    
    def ExprestringPrime(self):
        """Exprestring' -> plus Valorstring | ε"""
        if self.current == "PLUS":
            self.advance()
            return self.Valorstring()
        return True  # ε
    
    # ========== General Expression ==========
    def Expression(self):
        """Expression -> id Expression'"""
        if not self.match("ID"):
            return self.error("ID")
        return self.ExpressionPrime()
    
    def ExpressionPrime(self):
        """Expression' -> Usfun | Simb Valorexp | ε"""
        if self.current == "DELIM_LPAREN":
            return self.Usfun()
        elif self.current in ["PLUS", "MINUS", "MULT", "DIV", "EXP", "MODULO"]:
            if not self.Simb():
                return False
            return self.Valorexp()
        return True  # ε
    
    # ========== Basic Statements ==========
    def Asig(self):
        """Asig -> id equal Asig' delim_line"""
        if not self.match("ID"):
            return self.error("ID")
        if not self.match("EQUAL"):
            return self.error("EQUAL")
        if not self.AsigPrime():
            return False
        if not self.match("DELIM_LINE"):
            return self.error("DELIM_LINE")
        return True
    
    def AsigPrime(self):
        """Asig' -> Expremath | Exprestring | Valorbool | Expression"""
        if self.current in ["DATA_INT", "DATA_DOUBLE"] or self.current in ["FUN_SQRT", "FUN_ABS", "FUN_LN", "FUN_EXP", "FUN_SEN", "FUN_COS", "FUN_ATAN", "FUN_TRUNC", "FUN_ROUND", "FUN_RAND"]:
            return self.Expremath()
        elif self.current == "DATA_STRING":
            return self.Exprestring()
        elif self.current in ["TRUE", "FALSE"]:
            return self.Valorbool()
        elif self.current == "ID":
            return self.Expression()
        else:
            return self.error("Expression")
    
    def Impr(self):
        """Impr -> write Impr' delim_line"""
        if not self.match("WRITE"):
            return self.error("WRITE")
        if not self.ImprPrime():
            return False
        if not self.match("DELIM_LINE"):
            return self.error("DELIM_LINE")
        return True
    
    def ImprPrime(self):
        """Impr' -> Valor Printmul | id Printmul"""
        if self.current in ["DATA_INT", "DATA_DOUBLE", "DATA_STRING", "TRUE", "FALSE"]:
            if not self.Valor():
                return False
            return self.Printmul()
        elif self.current == "ID":
            self.advance()
            return self.Printmul()
        else:
            return self.error("Value or ID")
    
    def Printmul(self):
        """Printmul -> delim_comma Printmul' Printmul | ε"""
        if self.current == "DELIM_COMMA":
            self.advance()
            if not self.PrintmulPrime():
                return False
            return self.Printmul()
        return True  # ε
    
    def PrintmulPrime(self):
        """Printmul' -> id | Valor"""
        if self.current == "ID":
            self.advance()
            return True
        elif self.current in ["DATA_INT", "DATA_DOUBLE", "DATA_STRING", "TRUE", "FALSE"]:
            return self.Valor()
        else:
            return self.error("ID or Value")
    
    def Lect(self):
        """Lect -> read id delim_line"""
        if not self.match("READ"):
            return self.error("READ")
        if not self.match("ID"):
            return self.error("ID")
        if not self.match("DELIM_LINE"):
            return self.error("DELIM_LINE")
        return True
    
    def Defi(self):
        """Defi -> definir id Typed delim_line"""
        if not self.match("DEFINIR"):
            return self.error("DEFINIR")
        if not self.match("ID"):
            return self.error("ID")
        if not self.Typed():
            return False
        if not self.match("DELIM_LINE"):
            return self.error("DELIM_LINE")
        return True
    
    # ========== Function Usage ==========
    def Usfun(self):
        """Usfun -> delim_lparen Varmul delim_rparen | ε"""
        if self.current == "DELIM_LPAREN":
            self.advance()
            if not self.Varmul():
                return False
            if not self.match("DELIM_RPAREN"):
                return self.error("DELIM_RPAREN")
            return True
        return True  # ε
    
    def Varmul(self):
        """Varmul -> id Varmul'"""
        if not self.match("ID"):
            return self.error("ID")
        return self.VarmulPrime()
    
    def VarmulPrime(self):
        """Varmul' -> delim_comma id Varmul' | ε"""
        if self.current == "DELIM_COMMA":
            self.advance()
            if not self.match("ID"):
                return self.error("ID")
            return self.VarmulPrime()
        return True  # ε
    
    # ========== Terminal Symbols ==========
    def Typed(self):
        """Typed -> int | real | bool | char | string"""
        if self.current in ["INT", "REAL", "BOOL", "CHAR", "STRING"]:
            self.advance()
            return True
        return self.error("INT, REAL, BOOL, CHAR, or STRING")
    
    def Simb(self):
        """Simb -> plus | minus | mult | div | exp | modulo"""
        if self.current in ["PLUS", "MINUS", "MULT", "DIV", "EXP", "MODULO"]:
            self.advance()
            return True
        return self.error("Operator")
    
    def Valor(self):
        """Valor -> data_int | data_double | data_string | true | false"""
        if self.current in ["DATA_INT", "DATA_DOUBLE", "DATA_STRING", "TRUE", "FALSE"]:
            self.advance()
            return True
        return self.error("Value")
    
    def Valornum(self):
        """Valornum -> data_int | data_double"""
        if self.current in ["DATA_INT", "DATA_DOUBLE"]:
            self.advance()
            return True
        return self.error("DATA_INT or DATA_DOUBLE")
    
    def Valorlog(self):
        """Valorlog -> id | Valornum"""
        if self.current == "ID":
            self.advance()
            return True
        elif self.current in ["DATA_INT", "DATA_DOUBLE"]:
            return self.Valornum()
        else:
            return self.error("ID or numeric value")
    
    def Valorexp(self):
        """Valorexp -> id | Valornum | data_string"""
        if self.current == "ID":
            self.advance()
            return True
        elif self.current in ["DATA_INT", "DATA_DOUBLE"]:
            return self.Valornum()
        elif self.current == "DATA_STRING":
            self.advance()
            return True
        else:
            return self.error("ID, numeric value, or string")
    
    def Valorstring(self):
        """Valorstring -> id | data_string"""
        if self.current in ["ID", "DATA_STRING"]:
            self.advance()
            return True
        return self.error("ID or DATA_STRING")
    
    def Valorbool(self):
        """Valorbool -> true | false"""
        if self.current in ["TRUE", "FALSE"]:
            self.advance()
            return True
        return self.error("TRUE or FALSE")
    
    def Opeasig(self):
        """Opeasig -> less | more | same | less_same | more_same | diff"""
        if self.current in ["LESS", "MORE", "SAME", "LESS_SAME", "MORE_SAME", "DIFF"]:
            self.advance()
            return True
        return self.error("Comparison operator")
    
    def Opelog(self):
        """Opelog -> and | or | not"""
        if self.current in ["AND", "OR", "NOT"]:
            self.advance()
            return True
        return self.error("Logical operator")
    
    # ========== Main Analysis Function ==========
    def analyze(self):
        """Start syntax analysis"""
        print("Iniciando análisis sintáctico...")
        success = self.Program()
        
        if success and self.current is None:
            print("✓ Análisis sintáctico completado exitosamente")
            return True
        elif success and self.current is not None:
            self.error("EOF")
            print(f"✗ Error: Tokens sobrantes después del análisis: {self.current}")
            return False
        else:
            print("✗ Análisis sintáctico falló")
            for error in self.errors:
                print(f"  {error}")
            return False


def inicia_sintactico(tokens_str):
    """
    Initialize syntax analyzer with token string
    
    Args:
        tokens_str: String of comma-separated tokens (e.g., "PROCESS,ID,DELIM_LKEY,...")
    
    Returns:
        bool: True if syntax is valid, False otherwise
    """
    tokens = tokens_str.split(',')
    analyzer = SyntaxAnalyzer(tokens)
    return analyzer.analyze()