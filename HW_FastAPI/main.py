from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

app = FastAPI(title = 'Простой калькулятор')

class OperationRequest(BaseModel):
    a: float
    b: float
    op: str

class ExpressionRequest(BaseModel):
    expression: str

class ExpressionResponse(BaseModel):
    expression: str
    result: Optional[float] = None

class Calculator:
    def __init__(self):
        self.current_expression = ""
        self.result = 0
    
    def calculate_simple(self, a: float, b: float, op: str) -> float:
        """Простое вычисление между двумя числами"""
        if op == '+':
            return a + b
        elif op == '-':
            return a - b
        elif op == '*':
            return a * b
        elif op == '/':
            if b == 0:
                raise ValueError("Деление на ноль")
            return a / b
        else:
            raise ValueError(f"Неподдерживаемая операция: {op}")
    
    def evaluate_expression(self, expression: str) -> float:
        """Вычисление выражения используя eval (простой способ)"""
        # Безопасная проверка выражения
        allowed_chars = set('0123456789.+-*/() ')
        if not all(c in allowed_chars for c in expression):
            raise ValueError("Выражение содержит запрещенные символы")
        
        try:
            return eval(expression)
        except ZeroDivisionError:
            raise ValueError("Деление на ноль")
        except:
            raise ValueError("Некорректное выражение")

calculator = Calculator()


# Эндпоинты API
@app.post("/calculate/simple", response_model=ExpressionResponse)
async def calculate_simple(request: OperationRequest):
    """Простое вычисление: a op b"""
    try:
        result = calculator.calculate_simple(request.a, request.b, request.op)
        expression = f"{request.a} {request.op} {request.b}"
        calculator.current_expression = expression
        calculator.result = result
        return ExpressionResponse(expression=expression, result=result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/expression", response_model=ExpressionResponse)
async def set_expression(request: ExpressionRequest):
    """Установка и вычисление сложного выражения"""
    try:
        result = calculator.evaluate_expression(request.expression)
        calculator.current_expression = request.expression
        calculator.result = result
        return ExpressionResponse(expression=request.expression, result=result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/expression/add-operation", response_model=ExpressionResponse)
async def add_operation(request: OperationRequest):
    """Добавление операции к текущему выражению"""
    if not calculator.current_expression:
        # Если выражения нет, создаем новое
        return await calculate_simple(request)
    
    try:
        # Добавляем операцию к текущему результату
        result = calculator.calculate_simple(calculator.result, request.b, request.op)
        new_expression = f"({calculator.current_expression}) {request.op} {request.b}"
        
        calculator.current_expression = new_expression
        calculator.result = result
        
        return ExpressionResponse(expression=new_expression, result=result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/expression", response_model=ExpressionResponse)
async def get_expression():
    """Просмотр текущего выражения"""
    return ExpressionResponse(
        expression=calculator.current_expression,
        result=calculator.result if calculator.current_expression else None
    )

@app.post("/expression/execute", response_model=ExpressionResponse)
async def execute_expression():
    """Выполнение текущего выражения"""
    if not calculator.current_expression:
        raise HTTPException(status_code=400, detail="Нет выражения для выполнения")
    
    try:
        result = calculator.evaluate_expression(calculator.current_expression)
        calculator.result = result
        return ExpressionResponse(expression=calculator.current_expression, result=result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/expression")
async def clear_expression():
    """Очистка текущего выражения"""
    calculator.current_expression = ""
    calculator.result = 0
    return {"message": "Выражение очищено"}

# Простые эндпоинты для отдельных операций
@app.get("/add")
async def add(a: float, b: float):
    """Сложение"""
    return {"result": a + b}

@app.get("/subtract")
async def subtract(a: float, b: float):
    """Вычитание"""
    return {"result": a - b}

@app.get("/multiply")
async def multiply(a: float, b: float):
    """Умножение"""
    return {"result": a * b}

@app.get("/divide")
async def divide(a: float, b: float):
    """Деление"""
    if b == 0:
        raise HTTPException(status_code=400, detail="Деление на ноль")
    return {"result": a / b}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

