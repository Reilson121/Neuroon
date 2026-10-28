# NEURON - Organiza os PDFs de "Design de Artefatos Digitais"
# em uma pasta por aula (formato esperado pelo DisciplineProcessor).
#
# Salvar em:
#   C:\Projeto Extensionista 2\NEURON\neuron-ai\scripts\organizar_design_artefatos.ps1
#
# O script COPIA os arquivos (os originais ficam intactos).
# Sem -Executar ele apenas MOSTRA o plano (simulacao).

param(
    [Parameter(Mandatory = $true)]
    [string]$Origem,

    [string]$RaizProjeto = "C:\Projeto Extensionista 2\NEURON\neuron-ai",

    [switch]$Executar
)

$ErrorActionPreference = "Stop"

$destinoBase = Join-Path $RaizProjeto "materiais_academicos\periodo_03\design_de_artefatos_digitais"

# Padrao (regex, sem diferenciar maiusculas) -> pasta de destino.
# Os padroes nao dependem de acentos, entao funcionam mesmo se
# o nome do arquivo vier com "Copia de" ou "Cópia de".
$plano = @(
    @{ Padrao = "Aula 01";    Pasta = "aula_01_introducao_ao_design" },
    @{ Padrao = "Aula02";     Pasta = "aula_02_ferramentas_visuais" },
    @{ Padrao = "Aula03";     Pasta = "aula_03_publico_alvo" },
    @{ Padrao = "AULA_04";    Pasta = "aula_04_comportamento_do_consumidor" },
    @{ Padrao = "Aula_05";    Pasta = "aula_05_design_de_interface" },
    @{ Padrao = "Aula_6";     Pasta = "aula_06_principios_de_design" },
    @{ Padrao = "Aula_07";    Pasta = "aula_07_design_de_interface_diagramacao" },
    @{ Padrao = "AULA_08";    Pasta = "aula_08_design_thinking" },
    @{ Padrao = "MATRIZ_CSD"; Pasta = "material_complementar_matriz_csd" }
)

if (-not (Test-Path -LiteralPath $Origem)) {
    throw "Pasta de origem nao encontrada: $Origem"
}

$pdfs = Get-ChildItem -LiteralPath $Origem -Filter *.pdf -File

Write-Host ""
if ($Executar) { Write-Host "MODO: EXECUTAR (copiando arquivos)" }
else           { Write-Host "MODO: SIMULACAO (nada sera copiado)" }
Write-Host "Origem : $Origem"
Write-Host "Destino: $destinoBase"
Write-Host ""

$problemas = 0

foreach ($item in $plano) {

    $encontrados = @($pdfs | Where-Object { $_.Name -match $item.Padrao })

    if ($encontrados.Count -ne 1) {
        Write-Warning ("Padrao '{0}': esperado 1 arquivo, encontrado {1}." -f $item.Padrao, $encontrados.Count)
        $problemas++
        continue
    }

    $arquivo = $encontrados[0]

    # Remove o prefixo "Copia de " e troca ".pptx.pdf" por ".pdf".
    $novoNome = $arquivo.Name -replace '^C\S+ de ', ''
    $novoNome = $novoNome -replace '\.pptx\.pdf$', '.pdf'

    $pastaDestino = Join-Path $destinoBase $item.Pasta
    $caminhoFinal = Join-Path $pastaDestino $novoNome

    Write-Host ("{0}" -f $arquivo.Name)
    Write-Host ("   -> {0}\{1}" -f $item.Pasta, $novoNome)

    if ($Executar) {
        if (Test-Path -LiteralPath $caminhoFinal) {
            Write-Host "   (ja existe, ignorado)"
            continue
        }
        New-Item -ItemType Directory -Force -Path $pastaDestino | Out-Null
        Copy-Item -LiteralPath $arquivo.FullName -Destination $caminhoFinal
    }
}

Write-Host ""
if ($problemas -gt 0) {
    Write-Warning "$problemas padrao(oes) com problema. Confira a pasta de origem."
}
elseif (-not $Executar) {
    Write-Host "Simulacao OK. Para copiar de verdade, rode novamente com -Executar."
}
else {
    Write-Host "Concluido."
}