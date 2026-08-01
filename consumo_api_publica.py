"""
consumo_api_publica.py
=======================
Exemplo de como um programa "conversa" com uma API pública.

Vamos usar a ViaCEP: você manda um CEP, ela devolve o endereço.
Não precisa de senha nem cadastro (API pública e gratuita).

Documentação: https://viacep.com.br/
"""

import requests  # biblioteca que faz requisições HTTP em Python


def buscar_endereco_por_cep(cep: str) -> dict:
    """
    Busca um endereço a partir do CEP usando a API pública ViaCEP.

    Passo a passo:
    1. Montamos a URL (o "endereço da cozinha do restaurante")
    2. Mandamos um GET (só queremos LER informação, não mudar nada)
    3. A resposta vem em JSON -> convertemos pra dicionário Python
    """
    cep_limpo = cep.replace("-", "").replace(".", "").strip()
    url = f"https://viacep.com.br/ws/{cep_limpo}/json/"

    resposta = requests.get(url, timeout=5)

    # status_code é o "código de resultado" que a API devolve.
    # 200 = deu tudo certo. Outros códigos = algo diferente aconteceu.
    if resposta.status_code != 200:
        raise Exception(f"A API respondeu com erro: {resposta.status_code}")

    dados = resposta.json()  # transforma o texto JSON em dicionário Python

    if dados.get("erro"):
        raise ValueError("CEP não encontrado.")

    return {
        "logradouro": dados.get("logradouro"),
        "bairro": dados.get("bairro"),
        "cidade": dados.get("localidade"),
        "estado": dados.get("uf"),
    }


if __name__ == "__main__":
    endereco = buscar_endereco_por_cep("01310-100")  # CEP da Av. Paulista, SP
    print("Endereço encontrado:")
    for chave, valor in endereco.items():
        print(f"  {chave}: {valor}")
