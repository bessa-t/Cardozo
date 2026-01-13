# src/main.py
import sys
import os
import customtkinter as ctk

# 1. Configuração de Caminhos (Boilerplate profissional)
# Garante que o Python enxerga a pasta 'src' como raiz, não importa de onde você rode
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

# 2. Importa a Janela (O Frontend)
from frontend.app_window import App

# 3. Bloco de Execução Principal
if __name__ == "__main__":
    # Configurações globais de aparência (Opcional, mas recomendado ficar aqui)
    ctk.set_appearance_mode("Dark")
    ctk.set_default_color_theme("blue")

    # Instancia a aplicação
    app = App()
    
    # Inicia o Loop de Eventos (O programa entra em suspensão aguardando cliques)
    app.mainloop()