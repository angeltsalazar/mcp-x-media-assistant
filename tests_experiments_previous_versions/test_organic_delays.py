#!/usr/bin/env python3
"""
Script de prueba para demostrar los tiempos de espera orgánicos implementados.
"""
import random
import time

def _get_organic_delay(base_delay: float = 1.5) -> float:
    """
    Calcula un tiempo de espera orgánico y aleatorio para simular comportamiento humano.
    """
    # Variación aleatoria del ±40% del tiempo base
    variation = random.uniform(-0.4, 0.6)  # -40% a +60% para mayor naturalidad
    delay = base_delay * (1 + variation)
    
    # Asegurar que esté dentro del rango deseado (1.0 - 2.5 segundos)
    delay = max(1.0, min(2.5, delay))
    
    # Ocasionalmente agregar pausas más largas (5% de probabilidad)
    if random.random() < 0.05:
        delay += random.uniform(1.0, 3.0)  # Pausa larga ocasional
        print(f"   ⏱️  Aplicando pausa larga: {delay:.2f}s")
    
    return delay

def _get_organic_scroll_delay() -> float:
    """
    Calcula un tiempo de espera orgánico para scrolls.
    """
    # Tiempo base más realista para scroll (2.5-4.5 segundos)
    base_delay = random.uniform(2.5, 4.5)
    
    # Ocasionalmente hacer pausas más largas (10% de probabilidad)
    if random.random() < 0.1:
        base_delay += random.uniform(1.0, 2.5)  # Pausa larga ocasional
        print(f"   ⏱️  Aplicando pausa de scroll larga: {base_delay:.2f}s")
    
    return base_delay

def test_delays():
    """Prueba los diferentes tipos de delays orgánicos."""
    print("🧪 Probando delays orgánicos implementados:")
    print("=" * 50)
    
    print("\n🔗 Delays para navegación entre URLs de imágenes:")
    for i in range(10):
        delay = _get_organic_delay()
        print(f"   URL {i+1}: {delay:.2f}s")
    
    print("\n📜 Delays para scrolls:")
    for i in range(5):
        delay = _get_organic_scroll_delay()
        print(f"   Scroll {i+1}: {delay:.2f}s")
    
    print("\n⚡ Resumen de rangos implementados:")
    print("   • Navegación entre URLs: 1.0-2.5s (con pausas largas ocasionales)")
    print("   • Scrolls: 2.5-4.5s (con pausas largas ocasionales)")
    print("   • Estabilización cada 3 scrolls: 3.5-6.0s")
    print("   • Pausa final: 2.5-4.0s")
    print("   • Carga de página: 1.5-3.0s")

if __name__ == "__main__":
    test_delays()
