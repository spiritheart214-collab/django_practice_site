from typing import Union


def add_numbers(num_a, num_b) -> Union[int, float]:
    """Функция складывает два числа"""
    result = round(num_a + num_b, 2)
    return result

