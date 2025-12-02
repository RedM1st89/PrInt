class SyntaxAnalyzer:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.current = self.tokens[0] if tokens else None
        self.errors = []
    
    # Avanza un token
    def advance(self):
        self.pos += 1
        if self.pos < len(self.tokens):
            self.current = self.tokens[self.pos]
        else:
            self.current = None
    
    # Checa el token - ahora compara con el tipo del Token
    def match(self, expected):
        if self.current and self.current.tipo == expected:
            self.advance()
            return True
        return False
    
    # Error mejorado que muestra línea
    def error(self, expected):
        linea = self.current.linea if self.current else "EOF"
        token_actual = self.current.tipo if self.current else "EOF"
        msg = f"Error en línea {linea}, posición {self.pos}: Se esperaba '{expected}', se encontró '{token_actual}'"
        self.errors.append(msg)
        return False
    
    # Inicio del programa
    def Program(self):
        if not self.Class():
            return False
        return self.ProgramPrime()
    
    def ProgramPrime(self):
        if self.current and self.current.tipo == "FUNCTION":
            if not self.Func():
                return False
            return self.ProgramPrime()
        return True
    
    def Class(self):
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
        if not self.Accon():
            return False
        return self.ContPrime()
    
    def ContPrime(self):
        if self.current and self.current.tipo in ["DEFINIR", "ID", "WRITE", "READ", "IF", "FOR", "REPEAT", "WHILE", "SWITCH"]:
            if not self.Accon():
                return False
            return self.ContPrime()
        return True
    
    def Accon(self):
        if not self.current:
            return self.error("Statement")
        
        tipo = self.current.tipo
        if tipo == "DEFINIR":
            return self.Defi()
        elif tipo == "ID":
            return self.Asig()
        elif tipo == "WRITE":
            return self.Impr()
        elif tipo == "READ":
            return self.Lect()
        elif tipo == "IF":
            return self.Condif()
        elif tipo == "FOR":
            return self.CycleFor()
        elif tipo == "REPEAT":
            return self.CycleRep()
        elif tipo == "WHILE":
            return self.CycleWhile()
        elif tipo == "SWITCH":
            return self.Multselec()
        else:
            return self.error("DEFINIR, ID, WRITE, READ, IF, FOR, REPEAT, WHILE, or SWITCH")
    
    def Condif(self):
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
        if self.current and self.current.tipo == "ELSE":
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
        elif self.current and self.current.tipo == "END_IF":
            self.advance()
            return True
        else:
            return self.error("ELSE or END_IF")
    
    def Func(self):
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
    
    def CycleWhile(self):
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
    
    def Multselec(self):
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
        if self.current and self.current.tipo == "DATA_INT":
            if not self.MultselecDoublePrime():
                return False
            return self.MultselecPrime()
        return True
    
    def MultselecDoublePrime(self):
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
    
    def Contblo(self):
        if not self.Acblo():
            return False
        return self.ContbloPrime()
    
    def ContbloPrime(self):
        if self.current and self.current.tipo in ["ID", "WRITE", "READ", "IF", "FOR", "REPEAT", "WHILE", "SWITCH"]:
            if not self.Acblo():
                return False
            return self.ContbloPrime()
        return True
    
    def Acblo(self):
        if not self.current:
            return self.error("Statement")
        
        tipo = self.current.tipo
        if tipo == "ID":
            return self.Asig()
        elif tipo == "WRITE":
            return self.Impr()
        elif tipo == "READ":
            return self.Lect()
        elif tipo == "IF":
            return self.Condif()
        elif tipo == "FOR":
            return self.CycleFor()
        elif tipo == "REPEAT":
            return self.CycleRep()
        elif tipo == "WHILE":
            return self.CycleWhile()
        elif tipo == "SWITCH":
            return self.Multselec()
        else:
            return self.error("ID, WRITE, READ, IF, FOR, REPEAT, WHILE, or SWITCH")
    
    def Contswi(self):
        if not self.Acswi():
            return False
        return self.ContswiPrime()
    
    def ContswiPrime(self):
        if self.current and self.current.tipo in ["ID", "WRITE", "READ", "IF", "FOR", "REPEAT", "WHILE"]:
            if not self.Acswi():
                return False
            return self.ContswiPrime()
        return True
    
    def Acswi(self):
        if not self.current:
            return self.error("Statement")
        
        tipo = self.current.tipo
        if tipo == "ID":
            return self.Asig()
        elif tipo == "WRITE":
            return self.Impr()
        elif tipo == "READ":
            return self.Lect()
        elif tipo == "IF":
            return self.Condif()
        elif tipo == "FOR":
            return self.CycleFor()
        elif tipo == "REPEAT":
            return self.CycleRep()
        elif tipo == "WHILE":
            return self.CycleWhile()
        else:
            return self.error("ID, WRITE, READ, IF, FOR, REPEAT, or WHILE")
    
    def Exprelog(self):
        if not self.Log():
            return False
        return self.ExprelogPrime()
    
    def ExprelogPrime(self):
        if self.current and self.current.tipo in ["AND", "OR", "NOT"]:
            if not self.Opelog():
                return False
            if not self.Log():
                return False
            return self.ExprelogPrime()
        return True
    
    def Log(self):
        if not self.current:
            return self.error("Expression")
        
        if self.current.tipo == "ID":
            self.advance()
            if not self.Opeasig():
                return False
            return self.Valorlog()
        elif self.current.tipo in ["DATA_INT", "DATA_DOUBLE"]:
            if not self.Valornum():
                return False
            if not self.Opeasig():
                return False
            return self.Valorlog()
        else:
            return self.error("ID, DATA_INT, or DATA_DOUBLE")
    
    def Expremath(self):
        if not self.current:
            return self.error("Expression")
        
        if self.current.tipo in ["DATA_INT", "DATA_DOUBLE"]:
            if not self.Valornum():
                return False
            return self.ExpremathPrime()
        elif self.current.tipo in ["FUN_SQRT", "FUN_ABS", "FUN_LN", "FUN_EXP", "FUN_SEN", "FUN_COS", "FUN_ATAN", "FUN_TRUNC", "FUN_ROUND", "FUN_RAND"]:
            return self.Mathfunc()
        else:
            return self.error("DATA_INT, DATA_DOUBLE, or Math Function")
    
    def ExpremathPrime(self):
        if self.current and self.current.tipo in ["PLUS", "MINUS", "MULT", "DIV", "EXP", "MODULO"]:
            if not self.Simb():
                return False
            return self.Valorlog()
        return True
    
    def Mathfunc(self):
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
        if self.current and self.current.tipo in ["FUN_SQRT", "FUN_ABS", "FUN_LN", "FUN_EXP", "FUN_SEN", "FUN_COS", "FUN_ATAN", "FUN_TRUNC", "FUN_ROUND", "FUN_RAND"]:
            self.advance()
            return True
        return self.error("Math Function")
    
    def Exprestring(self):
        if not self.match("DATA_STRING"):
            return self.error("DATA_STRING")
        return self.ExprestringPrime()
    
    def ExprestringPrime(self):
        if self.current and self.current.tipo == "PLUS":
            self.advance()
            return self.Valorstring()
        return True
    
    def Expression(self):
        if not self.match("ID"):
            return self.error("ID")
        return self.ExpressionPrime()
    
    def ExpressionPrime(self):
        if not self.current:
            return True
        
        if self.current.tipo == "DELIM_LPAREN":
            return self.Usfun()
        elif self.current.tipo in ["PLUS", "MINUS", "MULT", "DIV", "EXP", "MODULO"]:
            if not self.Simb():
                return False
            return self.Valorexp()
        return True
    
    def Asig(self):
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
        if not self.current:
            return self.error("Expression")
        
        tipo = self.current.tipo
        if tipo in ["DATA_INT", "DATA_DOUBLE"] or tipo in ["FUN_SQRT", "FUN_ABS", "FUN_LN", "FUN_EXP", "FUN_SEN", "FUN_COS", "FUN_ATAN", "FUN_TRUNC", "FUN_ROUND", "FUN_RAND"]:
            return self.Expremath()
        elif tipo == "DATA_STRING":
            return self.Exprestring()
        elif tipo in ["TRUE", "FALSE"]:
            return self.Valorbool()
        elif tipo == "ID":
            return self.Expression()
        else:
            return self.error("Expression")
    
    def Impr(self):
        if not self.match("WRITE"):
            return self.error("WRITE")
        if not self.ImprPrime():
            return False
        if not self.match("DELIM_LINE"):
            return self.error("DELIM_LINE")
        return True
    
    def ImprPrime(self):
        if not self.current:
            return self.error("Value or ID")
        
        if self.current.tipo in ["DATA_INT", "DATA_DOUBLE", "DATA_STRING", "TRUE", "FALSE"]:
            if not self.Valor():
                return False
            return self.Printmul()
        elif self.current.tipo == "ID":
            self.advance()
            return self.Printmul()
        else:
            return self.error("Value or ID")
    
    def Printmul(self):
        if self.current and self.current.tipo == "DELIM_COMMA":
            self.advance()
            if not self.PrintmulPrime():
                return False
            return self.Printmul()
        return True
    
    def PrintmulPrime(self):
        if not self.current:
            return self.error("ID or Value")
        
        if self.current.tipo == "ID":
            self.advance()
            return True
        elif self.current.tipo in ["DATA_INT", "DATA_DOUBLE", "DATA_STRING", "TRUE", "FALSE"]:
            return self.Valor()
        else:
            return self.error("ID or Value")
    
    def Lect(self):
        if not self.match("READ"):
            return self.error("READ")
        if not self.match("ID"):
            return self.error("ID")
        if not self.match("DELIM_LINE"):
            return self.error("DELIM_LINE")
        return True
    
    def Defi(self):
        if not self.match("DEFINIR"):
            return self.error("DEFINIR")
        if not self.match("ID"):
            return self.error("ID")
        if not self.Typed():
            return False
        if not self.match("DELIM_LINE"):
            return self.error("DELIM_LINE")
        return True
    
    def Usfun(self):
        if self.current and self.current.tipo == "DELIM_LPAREN":
            self.advance()
            if not self.Varmul():
                return False
            if not self.match("DELIM_RPAREN"):
                return self.error("DELIM_RPAREN")
            return True
        return True
    
    def Varmul(self):
        if not self.match("ID"):
            return self.error("ID")
        return self.VarmulPrime()
    
    def VarmulPrime(self):
        if self.current and self.current.tipo == "DELIM_COMMA":
            self.advance()
            if not self.match("ID"):
                return self.error("ID")
            return self.VarmulPrime()
        return True
    
    def Typed(self):
        if self.current and self.current.tipo in ["INT", "REAL", "BOOL", "CHAR", "STRING"]:
            self.advance()
            return True
        return self.error("INT, REAL, BOOL, CHAR, or STRING")
    
    def Simb(self):
        if self.current and self.current.tipo in ["PLUS", "MINUS", "MULT", "DIV", "EXP", "MODULO"]:
            self.advance()
            return True
        return self.error("Operator")
    
    def Valor(self):
        if self.current and self.current.tipo in ["DATA_INT", "DATA_DOUBLE", "DATA_STRING", "TRUE", "FALSE"]:
            self.advance()
            return True
        return self.error("Value")
    
    def Valornum(self):
        if self.current and self.current.tipo in ["DATA_INT", "DATA_DOUBLE"]:
            self.advance()
            return True
        return self.error("DATA_INT or DATA_DOUBLE")
    
    def Valorlog(self):
        if not self.current:
            return self.error("ID or numeric value")
        
        if self.current.tipo == "ID":
            self.advance()
            return True
        elif self.current.tipo in ["DATA_INT", "DATA_DOUBLE"]:
            return self.Valornum()
        else:
            return self.error("ID or numeric value")
    
    def Valorexp(self):
        if not self.current:
            return self.error("ID, numeric value, or string")
        
        if self.current.tipo == "ID":
            self.advance()
            return True
        elif self.current.tipo in ["DATA_INT", "DATA_DOUBLE"]:
            return self.Valornum()
        elif self.current.tipo == "DATA_STRING":
            self.advance()
            return True
        else:
            return self.error("ID, numeric value, or string")
    
    def Valorstring(self):
        if self.current and self.current.tipo in ["ID", "DATA_STRING"]:
            self.advance()
            return True
        return self.error("ID or DATA_STRING")
    
    def Valorbool(self):
        if self.current and self.current.tipo in ["TRUE", "FALSE"]:
            self.advance()
            return True
        return self.error("TRUE or FALSE")
    
    def Opeasig(self):
        if self.current and self.current.tipo in ["LESS", "MORE", "SAME", "LESS_SAME", "MORE_SAME", "DIFF"]:
            self.advance()
            return True
        return self.error("Comparison operator")
    
    def Opelog(self):
        if self.current and self.current.tipo in ["AND", "OR", "NOT"]:
            self.advance()
            return True
        return self.error("Logical operator")
    
    def analyze(self):
        success = self.Program()
        
        if success and self.current is None:
            return True
        elif success and self.current is not None:
            self.error("EOF")
            print(f"✗ Error: Tokens sobrantes después del análisis: {self.current.tipo}")
            return False
        else:
            print("D;")
            for error in self.errors:
                print(f"  {error}")
            return False


def inicia_sintactico(tokens_list):
    # Ahora recibe lista de objetos Token directamente
    analyzer = SyntaxAnalyzer(tokens_list)
    return analyzer.analyze()