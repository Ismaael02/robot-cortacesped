param(
    [Parameter(Mandatory = $true)]
    [string]$UsuarioGitHub,

    [string]$Repositorio = "robot-cortacesped"
)

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

Write-Host ""
Write-Host "=== Publicar en GitHub ===" -ForegroundColor Cyan
Write-Host ""

Write-Host "1/5  Generando el sitio..."
python build.py

Write-Host "2/5  Preparando el repositorio..."
if (-not (Test-Path ".git")) { git init | Out-Null }
git config user.name $UsuarioGitHub
git config user.email "$UsuarioGitHub@users.noreply.github.com"
git config credential.helper manager
git branch -M main

Write-Host "3/5  Añadiendo archivos..."
git add -A
$pending = git status --porcelain
if ($pending) {
    git commit -m "Sitio de robots cortacesped: comparativa, calculadora y guias" | Out-Null
    Write-Host "     Commit creado."
} else {
    Write-Host "     Sin cambios nuevos que subir."
}

Write-Host "4/5  Configurando el remoto..."
$url = "https://github.com/$UsuarioGitHub/$Repositorio.git"
$remotos = git remote
if ($remotos -contains "origin") {
    git remote set-url origin $url
} else {
    git remote add origin $url
}

Write-Host "5/5  Subiendo a GitHub..."
git push -u origin main

Write-Host ""
Write-Host "Listo. El código ya está en $url" -ForegroundColor Green
Write-Host "Ahora conecta ese repositorio en Cloudflare Pages (ver README)." -ForegroundColor Green
Write-Host ""
