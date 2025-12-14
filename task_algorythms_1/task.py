import json
import re
from difflib import SequenceMatcher
from typing import Dict, List, Set

# Параметры алгоритма
SIMILARITY_THRESHOLD = 0.8
USE_PREPROCESSING = True

def normalize_text(text: str) -> str:
    """
    Нормализация текста для сравнения.
    """
    if not USE_PREPROCESSING:
        return text.lower()
    
    text = text.lower()
    
    # Цвета (английские -> русские)
    color_mapping = {
        'black': 'черный',
        'blue': 'синий', 
        'red': 'красный',
        'green': 'зеленый',
        'white': 'белый',
        'silver': 'серебристый',
        'gold': 'золотой',
        'yellow': 'желтый',
        'gray': 'серый',
        'grey': 'серый',
        'pink': 'розовый'
    }
    
    for eng_color, ru_color in color_mapping.items():
        text = text.replace(eng_color, ru_color)
    
    # Единицы измерения и сокращения
    unit_mapping = {
        'gb': 'гб',
        'gb.': 'гб',
        'mb': 'мб',
        'kb': 'кб',
        'tb': 'тб',
        'inch': 'дюйм',
        '"': 'дюйм',
        'дюймов': 'дюйм',
        'дюйма': 'дюйм',
        'mm': 'мм',
        'cm': 'см',
        'kg': 'кг',
        'g': 'г',
        'ml': 'мл',
        'l': 'л',
        'pro': 'про',
        'plus': 'плюс',
        '+': 'плюс'
    }
    
    for unit, replacement in unit_mapping.items():
        pattern = r'(^|\s)' + re.escape(unit) + r'($|\s)'
        text = re.sub(pattern, f'\\1{replacement}\\2', text)
    
    # Нормализация брендов
    brand_mapping = {
        'xiaomi': 'xiaomi',
        'xiao mi': 'xiaomi',
        'redmi': 'xiaomi redmi',
        'mi ': 'xiaomi ',
        'huawei': 'huawei',
        'huawei': 'huawei',
        'honor': 'huawei honor',
        'irbis': 'irbis',
        'samsung': 'samsung',
        'apple': 'apple',
        'iphone': 'apple iphone'
    }
    
    for variant, normalized in brand_mapping.items():
        if variant in text:
            text = text.replace(variant, normalized)
    
    # Синонимы и общие замены
    synonym_mapping = {
        'смартфон': 'телефон',
        'телефон': 'телефон',
        'phone': 'телефон',
        'smartphone': 'телефон',
        'мобильный телефон': 'телефон',
        'мобильник': 'телефон',
        'андроид': 'android',
        'android': 'android',
        'робот-пылесос': 'робот пылесос',
        'робот пылесос': 'робот пылесос',
        'vacuum cleaner': 'робот пылесос',
        'vacuum': 'пылесос',
        'пылесос-робот': 'робот пылесос',
        'часы': 'часы',
        'watch': 'часы',
        'часы smart': 'часы',
        'smart watch': 'часы',
        'планшет': 'планшет',
        'tablet': 'планшет',
        'планшетный компьютер': 'планшет'
    }
    
    for synonym, replacement in synonym_mapping.items():
        if synonym in text:
            text = text.replace(synonym, replacement)
    
    text = re.sub(r'[^\w\s\/\+]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    
    stop_words = {'и', 'в', 'на', 'с', 'для', 'по', 'из', 'от', 'до', 'со', 'под', 'над', 'при'}
    words = text.split()
    filtered_words = [word for word in words if word not in stop_words]
    
    return ' '.join(filtered_words)

def tokenize_name(name: str) -> Set[str]:
    """
    Разбивает название на токены.
    """
    tokens = re.split(r'[\s\/\+]', name)
    
    valid_tokens = set()
    for token in tokens:
        if token and len(token) > 1:
            token = re.sub(r'(\d+)(гб|мб|кб|тб|дюйм|мм|см)?', r'\1', token)
            valid_tokens.add(token)
    
    return valid_tokens

def calculate_jaccard_similarity(set1: Set[str], set2: Set[str]) -> float:
    """
    Вычисляет коэффициент Жаккара для двух множеств.
    """
    if not set1 or not set2:
        return 0.0
    
    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))
    
    return intersection / union if union > 0 else 0.0

def calculate_similarity(name1: str, name2: str) -> float:
    """
    Вычисляет общую схожесть двух названий.
    """
    norm1 = normalize_text(name1)
    norm2 = normalize_text(name2)
    
    if norm1 == norm2:
        return 1.0
    
    sequence_similarity = SequenceMatcher(None, norm1, norm2).ratio()
    
    tokens1 = tokenize_name(norm1)
    tokens2 = tokenize_name(norm2)
    jaccard_similarity = calculate_jaccard_similarity(tokens1, tokens2)
    
    has_specs_match = has_matching_specifications(tokens1, tokens2)
    
    combined_similarity = 0.3 * sequence_similarity + 0.7 * jaccard_similarity
    
    if has_specs_match:
        combined_similarity = min(1.0, combined_similarity + 0.15)
    
    return combined_similarity

def has_matching_specifications(tokens1: Set[str], tokens2: Set[str]) -> bool:
    """
    Проверяет совпадение технических характеристик.
    """
    spec_patterns = [
        r'^\d+/\d+$',
        r'^\d+\.\d+$',
        r'^\d+дюйм$',
        r'^\d+гб$',
        r'^\d+мм$',
        r'^\d+$',
    ]
    
    specs1 = set()
    specs2 = set()
    
    for token in tokens1:
        for pattern in spec_patterns:
            if re.match(pattern, token):
                specs1.add(token)
                break
    
    for token in tokens2:
        for pattern in spec_patterns:
            if re.match(pattern, token):
                specs2.add(token)
                break
    
    return len(specs1.intersection(specs2)) > 0

def load_catalog(filename: str) -> Dict[str, str]:
    """
    Загружает каталог из файла.
    """
    catalog = {}
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    if '\t' in line:
                        parts = line.split('\t', 1)
                    else:
                        parts = line.split(' ', 1)
                    
                    if len(parts) == 2:
                        product_id = parts[0].strip()
                        product_name = parts[1].strip()
                        catalog[product_id] = product_name
    except FileNotFoundError:
        print(f"Файл {filename} не найден!")
    return catalog

def find_duplicates(new_items: Dict[str, str], catalog: Dict[str, str]) -> Dict[str, List[Dict]]:
    """
    Находит дубликаты для новых товаров.
    """
    results = {}
    
    for new_id, new_name in new_items.items():
        duplicates = []
        
        for catalog_id, catalog_name in catalog.items():
            similarity = calculate_similarity(new_name, catalog_name)
            
            if similarity >= SIMILARITY_THRESHOLD:
                duplicates.append({
                    "catalog_id": catalog_id,
                    "similarity_score": round(similarity, 2)
                })
        
        duplicates.sort(key=lambda x: x["similarity_score"], reverse=True)
        results[new_id] = duplicates
    
    return results

def main():
    catalog = load_catalog('task_algorythms_1/catalog.txt')
    new_items = load_catalog('task_algorythms_1/new_items.txt')
    
    duplicates = find_duplicates(new_items, catalog)
    
    with open('duplicates.json', 'w', encoding='utf-8') as f:
        json.dump(duplicates, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
