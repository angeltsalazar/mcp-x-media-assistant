#!/usr/bin/env python3
"""
Debug específico para el problema de name=360x360
"""

import re

def debug_regex():
    test_url = "https://pbs.twimg.com/media/GpoTbA-XwAAm4-O?format=jpg&name=360x360"
    print(f"URL original: {test_url}")
    
    # Probar diferentes regex paso a paso
    regex_tests = [
        (r'&?name=(?:360x360|small|medium|thumb|orig)(?=&|$)', 'Eliminar &name=360x360'),
        (r'\?name=(?:360x360|small|medium|thumb|orig)(?=&|$)', 'Eliminar ?name=360x360'),
        (r'name=360x360', 'Simple name=360x360'),
        (r'&name=360x360', 'Con & al inicio'),
        (r'\?name=360x360', 'Con ? al inicio'),
    ]
    
    for regex, desc in regex_tests:
        result = re.sub(regex, '', test_url)
        match = re.search(regex, test_url)
        print(f"\n{desc}:")
        print(f"  Regex: {regex}")
        print(f"  Match: {match}")
        print(f"  Resultado: {result}")
    
    print("\n" + "="*50)
    print("PROCESAMIENTO COMPLETO:")
    
    url = test_url
    print(f"1. Original: {url}")
    
    # Paso 1
    url = re.sub(r'&?name=(?:360x360|small|medium|thumb|orig)(?=&|$)', '', url)
    print(f"2. Después de regex 1: {url}")
    
    # Paso 2
    url = re.sub(r'\?name=(?:360x360|small|medium|thumb|orig)(?=&|$)', '?', url)
    print(f"3. Después de regex 2: {url}")
    
    # Paso 3
    url = re.sub(r'&?[a-zA-Z0-9_]+=(?:medium|small|thumb)(?=&|$)', '', url)
    print(f"4. Después de regex 3: {url}")
    
    # Limpiar sintaxis
    url = re.sub(r'\?&', '?', url)
    print(f"5. Después de \?&: {url}")
    
    url = re.sub(r'&+', '&', url)
    print(f"6. Después de &+: {url}")
    
    url = re.sub(r'\?$', '', url)
    print(f"7. Final: {url}")

if __name__ == "__main__":
    debug_regex()
