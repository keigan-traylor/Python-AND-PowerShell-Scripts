$src = "source directory which is the CD drive for us"
$dst = "destination directory which is the USB drive for us"
#using get-childitem to get all files and folders in the source directory (our CD drive)
#we get all items maintaining the folder structure and file type then we force install it on the dest drive
Get-ChildItem -Path $src -Recurse | ForEach-Object {
    $destination = $_.FullName.Replace($src, $dst)
    if (!($_.PSIsContainer)) {
        if (!(Test-Path $(Split-Path $destination -Parent))) {
            New-Item -ItemType Directory -Path $(Split-Path $destination -Parent) | Out-Null
        }
        Copy-Item$_.FullName -Destination $destination
    }
}