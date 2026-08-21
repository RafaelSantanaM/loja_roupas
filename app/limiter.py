"""
app/limiter.py
================
Existe SÓ por um motivo técnico: app/main.py precisa registrar o
limiter na aplicação, e os routers (app/routers/*.py) precisam usar
@limiter.limit(...) nos endpoints -- ambos precisam do MESMO objeto.

Se o limiter fosse criado dentro de main.py, e os routers tentassem
"from app.main import limiter", teríamos uma IMPORTAÇÃO CIRCULAR:
main.py importa os routers (para registrá-los), e os routers
importariam main.py de volta -- o Python não consegue resolver esse
ciclo. Colocando o limiter num arquivo neutro, os dois lados importam
dali, sem depender um do outro.
"""

from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
