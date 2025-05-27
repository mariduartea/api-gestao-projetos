# para executar: .\docker-cleanup.ps1
Write-Host "Limpando containers parados..."
docker container prune -f

Write-Host "Limpando imagens não utilizadas..."
docker image prune -a -f

Write-Host "Limpando volumes não utilizados..."
docker volume prune -f

Write-Host "Limpando redes não utilizadas..."
docker network prune -f

Write-Host "Limpando tudo (system prune)..."
docker system prune -a --volumes -f

Write-Host "Limpeza Docker finalizada!"