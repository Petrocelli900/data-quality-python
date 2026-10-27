# Decisões técnicas

csv.reader em modo estrito exige cabeçalhos correspondentes ao esquema, sem duplicatas. Números de registros começam em 1 e não são números de linhas físicas: campos podem conter quebras de linha.

Tipos: text, integer, decimal e email. Decimais não finitos são rejeitados. E-mail tem validação sintática simplificada, sem verificar entrega. Espaços externos são removidos. Unicidade compara texto: 01 e 1 são diferentes.

Saídas: 0 válido, 1 problemas nos dados, 2 leitura ou esquema inválido. Relatório inclui códigos e coluna sem copiar valores pessoais.

Limitações: separador fixo vírgula; não implementa JSON Schema completo. Conjuntos de unicidade e problemas crescem com o arquivo. Próximas melhorias: limite de problemas e unicidade com SQLite.
