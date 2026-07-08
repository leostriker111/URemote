# Instala uremote portable: clona a ~\URemote y agrega al PATH del usuario.
$ErrorActionPreference = "Stop"
$destino = Join-Path $HOME "URemote"

if (Test-Path (Join-Path $destino ".git")) {
    Write-Host "actualizando $destino"
    git -C $destino pull --ff-only
} else {
    git clone https://github.com/leostriker111/uremote $destino
}

$path = [Environment]::GetEnvironmentVariable("Path", "User")
if ($path -notlike "*$destino*") {
    [Environment]::SetEnvironmentVariable("Path", "$path;$destino", "User")
    Write-Host "agregado al PATH de usuario (abre una terminal nueva)"
}
Write-Host "listo: prueba con  uremote -h"
