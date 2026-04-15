# Create assets/videos folder if not exists
$videoFolder = "assets/videos"
if (!(Test-Path $videoFolder)) {
    New-Item -ItemType Directory -Path $videoFolder | Out-Null
}

$videos = @(
    "https://www.youtube.com/watch?v=Tt4cUdQMh7I",   # Motion in One Dimension
    "https://www.youtube.com/watch?v=JGO_zDWmkvk",   # Newton's Laws
    "https://www.youtube.com/watch?v=w4QFJb9a8vo",   # Work Energy Power
    "https://www.youtube.com/watch?v=H0ga_Hvc_MY",   # Waves & Oscillations
    "https://www.youtube.com/watch?v=Af9lRX4xsr0",   # Gravitation
    "https://www.youtube.com/watch?v=LPX6wwhpA38",   # Rotational Motion
    "https://www.youtube.com/watch?v=LL54E5CzQ-A",   # Thermodynamics
    "https://www.youtube.com/watch?v=TFlVWf8JX4A",   # Electric Charges & Fields
    "https://www.youtube.com/watch?v=wtHi6kgA0-s",   # Chemistry Thermodynamics
    "https://www.youtube.com/watch?v=EMDrb2LqL7E",   # Atomic Structure
    "https://www.youtube.com/watch?v=b8fqBWGmpe4",   # Organic Basics
    "https://www.youtube.com/watch?v=7qOFtL3VEBc",   # Chemical Kinetics
    "https://www.youtube.com/watch?v=zvBeAaRGo3U",   # Chemical Bonding
    "https://www.youtube.com/watch?v=fwk3grEcSVs",   # Chemical Equilibrium
    "https://www.youtube.com/watch?v=i4lTvRNkRP4",   # Solutions
    "https://www.youtube.com/watch?v=XyO8ZvLDJSk",   # Redox Reactions
    "https://www.youtube.com/watch?v=eK-NCfvTtIE",   # Cell Structure
    "https://www.youtube.com/watch?v=NR3779ef9yQ",   # Genetics
    "https://www.youtube.com/watch?v=9dAcEBXAFoo",   # Ecology
    "https://www.youtube.com/watch?v=6qk_LTVXZ2w",   # Human Physiology
    "https://www.youtube.com/watch?v=y9BLCfcUcFg",   # Plant Physiology
    "https://www.youtube.com/watch?v=YO244P1e9QM",   # Biomolecules
    "https://www.youtube.com/watch?v=7VM9YxmULuo",   # Evolution
    "https://www.youtube.com/watch?v=-ekRRuSa_UQ"    # Reproduction
)

foreach ($url in $videos) {
    Write-Host "Downloading $url ..."
    .\yt-dlp.exe -f "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best" -o "$videoFolder\%(title)s.%(ext)s" $url
}

Write-Host "ALL VIDEOS DOWNLOADED!"
