#!/usr/bin/env python3
"""
Punto de entrada principal del Automatizador MUDE.
Módulos disponibles: Colocaciones (BHD/Banreservas) y Monitor de Pagarés.
"""

import sys
import os

# Agregar el directorio actual al PYTHONPATH para que los imports funcionen
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gui.menu_principal import MenuPrincipal

def main():
    app = MenuPrincipal()
    app.mainloop()

if __name__ == '__main__':
    main()
