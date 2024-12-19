def get_text(dice):
    """Возвращает текстовое представление кубиков"""
    if not dice:
        return "Нет кубиков"
    return " + ".join(f"d{num}" for num in dice) + f' + {str(5)}'
    
print(get_text([1]))  # Expected output: "1 + 2 + 3 + 4 + 5"

