from pydantic import BaseModel, Field

class BulaSimplificada(BaseModel):
    indicacao: str = Field(description="1. Para que este medicamento é indicado?")
    funcionamento: str = Field(description="2. Como este medicamento funciona?")
    contraindicacoes: str = Field(description="3. Quando não devo usar este medicamento?")
    precaucoes_populacoes_especiais: str = Field(description="Avisos específicos para gestantes, lactantes, idosos, crianças e doenças prévias.")
    interacoes_medicamentosas: str = Field(description="O que saber antes de usar (interação com alimentos, álcool e outros remédios).")
    armazenamento: str = Field(description="4. Onde, como e por quanto tempo posso guardar este medicamento?")
    posologia_uso: str = Field(description="5. Como devo usar este medicamento? (Converta tabelas em listas legíveis).")
    esquecimento: str = Field(description="6. O que devo fazer quando eu me esquecer de usar este medicamento?")
    efeitos_colaterais: str = Field(description="7. Quais os males que este medicamento pode me causar?")
    superdose: str = Field(description="8. O que fazer se alguém usar uma quantidade maior do que a indicada?")
    avisos_seguranca: str = Field(description="Alertas obrigatórios (ex: 'Não se automedique', 'Converse com seu médico').")
