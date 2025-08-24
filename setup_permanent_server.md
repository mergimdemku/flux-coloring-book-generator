# PC als permanenter Entwicklungsserver (wie vast.ai)

## Was du brauchst:

### Option 1: NGROK (Einfachste Lösung) - Kostenlos
```bash
# 1. Ngrok installieren
# Download von: https://ngrok.com/download

# 2. Account erstellen (kostenlos)
# https://dashboard.ngrok.com/signup

# 3. Token authentifizieren
ngrok config add-authtoken YOUR_TOKEN

# 4. SSH Tunnel erstellen (für Terminal-Zugriff)
ngrok tcp 22

# 5. VS Code Server Tunnel
ngrok http 8080
```

### Option 2: TAILSCALE (Professioneller) - Kostenlos für Personal Use
```bash
# 1. Tailscale installieren
# Windows: https://tailscale.com/download/windows

# 2. Auf beiden Geräten installieren (PC + Laptop)

# 3. Einloggen mit gleichem Account

# Dein PC bekommt eine feste IP wie: 100.x.x.x
# Immer erreichbar, egal wo du bist
```

### Option 3: VS CODE REMOTE TUNNELS (Microsoft Official)
```bash
# Auf deinem PC:
# 1. VS Code installieren
# 2. Terminal öffnen

code tunnel

# Gibt dir eine URL wie:
# https://vscode.dev/tunnel/YOUR-PC-NAME

# Von überall erreichbar!
```

## Schritt-für-Schritt Setup:

### 1. VS Code Remote Tunnel (EMPFOHLEN - Genau wie vast.ai!)

**Auf deinem PC (Windows):**
```powershell
# PowerShell als Admin öffnen

# 1. VS Code CLI installieren
winget install Microsoft.VisualStudioCode

# 2. Remote Tunnel Extension
code --install-extension ms-vscode.remote-server

# 3. Tunnel starten
code tunnel --name mein-flux-pc

# Gibt dir:
# https://vscode.dev/tunnel/mein-flux-pc/D:/CLAUDE/Kids_App_Painting_Books
```

**Auf deinem Laptop:**
- Browser öffnen
- Zu der URL gehen
- Mit GitHub/Microsoft Account einloggen
- FERTIG! Du hast vollen Zugriff wie bei vast.ai

### 2. SSH Server auf Windows PC

```powershell
# PowerShell als Admin

# OpenSSH Server installieren
Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0

# Starten
Start-Service sshd
Set-Service -Name sshd -StartupType 'Automatic'

# Firewall Regel
New-NetFirewallRule -Name sshd -DisplayName 'OpenSSH Server (sshd)' -Enabled True -Direction Inbound -Protocol TCP -Action Allow -LocalPort 22
```

### 3. Port Forwarding im Router

```
Router Admin Panel (meist 192.168.1.1):
- Port Forwarding / Virtual Server
- External Port: 22 (SSH)
- Internal IP: Deine PC IP (z.B. 192.168.1.100)
- Internal Port: 22
- Protocol: TCP

Für FLUX Web:
- External Port: 5000
- Internal Port: 5000
- Protocol: TCP
```

### 4. DynDNS für feste Adresse

**Kostenlose Services:**
- no-ip.com
- duckdns.org
- dynu.com

```bash
# Beispiel mit DuckDNS:
# 1. Account auf duckdns.org
# 2. Domain erstellen: meinflux.duckdns.org
# 3. Update Script auf PC:

# Windows Task Scheduler:
curl "https://www.duckdns.org/update?domains=meinflux&token=YOUR_TOKEN&ip="
```

## KOMPLETTE LÖSUNG - Alles in einem Script:

### setup_dev_server.bat
```batch
@echo off
echo ========================================
echo PC ALS ENTWICKLUNGSSERVER SETUP
echo ========================================

REM 1. SSH Server aktivieren
powershell -Command "Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0"
powershell -Command "Start-Service sshd"
powershell -Command "Set-Service -Name sshd -StartupType 'Automatic'"

REM 2. VS Code Tunnel
echo.
echo Starting VS Code Tunnel...
code tunnel --name flux-dev-pc

REM URL wird angezeigt
```

### auto_start.bat (Im Autostart Ordner)
```batch
@echo off
REM In Autostart Ordner legen:
REM C:\Users\%USERNAME%\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup

REM SSH Server
net start sshd

REM VS Code Tunnel
start /min cmd /c "code tunnel --name flux-dev-pc"

REM FLUX Server
cd /d D:\CLAUDE\Kids_App_Painting_Books
start /min cmd /c "python server_rtx3070.py"

REM Ngrok (falls benutzt)
start /min cmd /c "ngrok tcp 22"
```

## Zugriff von überall:

### Mit VS Code (wie vast.ai):
```
https://vscode.dev/tunnel/flux-dev-pc
```

### Mit SSH:
```bash
ssh username@meinflux.duckdns.org
# oder mit ngrok:
ssh username@0.tcp.ngrok.io -p 12345
```

### FLUX Web Interface:
```
http://meinflux.duckdns.org:5000
# oder mit ngrok:
http://xyz.ngrok.io
```

## Sicherheit:

### Windows Defender Firewall:
```powershell
# Ports öffnen
New-NetFirewallRule -DisplayName "FLUX Server" -Direction Inbound -Protocol TCP -LocalPort 5000 -Action Allow
New-NetFirewallRule -DisplayName "SSH" -Direction Inbound -Protocol TCP -LocalPort 22 -Action Allow
```

### Starke Passwörter:
```powershell
# Windows User Passwort ändern
net user %USERNAME% *
```

### Nur bestimmte IPs erlauben (optional):
```powershell
New-NetFirewallRule -DisplayName "SSH Limited" -Direction Inbound -Protocol TCP -LocalPort 22 -Action Allow -RemoteAddress "1.2.3.4"
```

## Empfehlung für dich:

**BESTE LÖSUNG: VS Code Remote Tunnels**
- Kostenlos
- Sicher (Microsoft)
- Keine Port-Forwarding nötig
- Funktioniert wie vast.ai
- Von überall erreichbar

**ALTERNATIVE: Tailscale**
- Eigenes VPN
- Super sicher
- Einfach zu nutzen
- Kostenlos für Personal Use