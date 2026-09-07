# AI Quiz Evaluator - Sleek Horizontal Setup Installer

[void][System.Reflection.Assembly]::LoadWithPartialName("PresentationFramework")
[void][System.Reflection.Assembly]::LoadWithPartialName("PresentationCore")
[void][System.Reflection.Assembly]::LoadWithPartialName("WindowsBase")

$xaml = @"
<Window xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
        xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
        Title="AI Quiz Evaluator Setup" Height="220" Width="640"
        WindowStartupLocation="CenterScreen" ResizeMode="NoResize"
        Background="#FFFFFF" Foreground="#0F172A" FontFamily="Segoe UI">
    <Grid Margin="24">
        <Grid.RowDefinitions>
            <RowDefinition Height="Auto"/>
            <RowDefinition Height="Auto"/>
            <RowDefinition Height="Auto"/>
            <RowDefinition Height="Auto"/>
        </Grid.RowDefinitions>

        <!-- Header Bar -->
        <Grid Grid.Row="0" Margin="0,0,0,16">
            <StackPanel HorizontalAlignment="Left">
                <TextBlock Text="AI Quiz Evaluator Setup" FontSize="18" FontWeight="SemiBold" Foreground="#0F172A"/>
                <TextBlock Text="Setting up environment, dependencies, and AI engine..." FontSize="12" Foreground="#64748B" Margin="0,2,0,0"/>
            </StackPanel>
            <TextBlock x:Name="PercentText" Text="0%" FontSize="20" FontWeight="Bold" Foreground="#2563EB" HorizontalAlignment="Right" VerticalAlignment="Center"/>
        </Grid>

        <!-- Horizontal Progress Bar Track -->
        <Border Grid.Row="1" Height="12" CornerRadius="6" Background="#F1F5F9" BorderBrush="#E2E8F0" BorderThickness="1" Margin="0,0,0,14">
            <Grid>
                <Border x:Name="ProgressBarFill" HorizontalAlignment="Left" Width="0" CornerRadius="5" Background="#2563EB"/>
            </Grid>
        </Border>

        <!-- Activity Readout Line -->
        <Border Grid.Row="2" Background="#F8FAFC" CornerRadius="6" BorderBrush="#E2E8F0" BorderThickness="1" Padding="12,8" Margin="0,0,0,12">
            <Grid>
                <TextBlock x:Name="StatusText" Text="Initializing setup installer..." FontSize="12" FontWeight="Medium" Foreground="#334155" HorizontalAlignment="Left" TextWrapping="NoWrap"/>
                <TextBlock x:Name="LogText" Text="Starting..." FontSize="11" Foreground="#94A3B8" HorizontalAlignment="Right" TextWrapping="NoWrap"/>
            </Grid>
        </Border>

        <!-- Footer -->
        <Grid Grid.Row="3">
            <TextBlock Text="AI Quiz Evaluator Setup Wizard" FontSize="11" Foreground="#94A3B8" HorizontalAlignment="Left"/>
            <TextBlock Text="Please wait until launch..." FontSize="11" Foreground="#94A3B8" HorizontalAlignment="Right"/>
        </Grid>
    </Grid>
</Window>
"@

$reader = (New-Object System.Xml.XmlNodeReader ([xml]$xaml))
$window = [System.Windows.Markup.XamlReader]::Load($reader)

$statusLabel = $window.FindName('StatusText')
$percentLabel = $window.FindName('PercentText')
$barFill = $window.FindName('ProgressBarFill')
$logBlock = $window.FindName('LogText')

function Update-UI {
    param (
        [int]$percent,
        [string]$status,
        [string]$logMessage,
        [string]$barColor = "#2563EB"
    )
    if ($window -and $statusLabel) {
        $statusLabel.Text = $status
        $percentLabel.Text = "$percent%"
        $totalWidth = 592
        $targetWidth = [math]::Max(0, [math]::Min($totalWidth, ($percent / 100) * $totalWidth))
        
        # Smooth animation transition
        $anim = New-Object System.Windows.Media.Animation.DoubleAnimation
        $anim.To = $targetWidth
        $anim.Duration = [TimeSpan]::FromMilliseconds(300)
        $barFill.BeginAnimation([System.Windows.Controls.Border]::WidthProperty, $anim)

        if ($barColor) {
            try {
                $bc = New-Object System.Windows.Media.BrushConverter
                $barFill.Background = $bc.ConvertFromString($barColor)
            } catch {}
        }

        if ($logMessage) {
            $logBlock.Text = $logMessage
        }
        [System.Windows.Threading.Dispatcher]::CurrentDispatcher.Invoke([action]{}, [System.Windows.Threading.DispatcherPriority]::Background)
    }
}

function Stop-InstallerWithError {
    param (
        [int]$percent,
        [string]$status,
        [string]$errorMessage
    )
    $timer.Stop()
    Update-UI $percent "[ERROR] $status" "ERROR: $errorMessage" "#EF4444"
}

function Test-ValidPython {
    param ([string]$pyPath)
    if (-not $pyPath) { return $false }
    # Ignore WindowsApps Microsoft Store execution aliases
    if ($pyPath -like "*WindowsApps*") { return $false }
    if ($pyPath -ne "py" -and -not (Test-Path $pyPath)) { return $false }
    
    try {
        if ($pyPath -eq "py") {
            $out = & py -3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>&1
        } else {
            $out = & "$pyPath" -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>&1
        }
        if ($LASTEXITCODE -eq 0 -and $out -match '^(\d+)\.(\d+)') {
            $major = [int]$Matches[1]
            $minor = [int]$Matches[2]
            # Django 5.x requires Python 3.10 or higher
            if ($major -eq 3 -and $minor -ge 10) {
                return $true
            }
        }
    } catch {}
    return $false
}

function Get-SystemPythonPath {
    # 1. Check 'python' command in PATH
    $cmd = Get-Command python -ErrorAction SilentlyContinue
    if ($cmd -and (Test-ValidPython $cmd.Source)) {
        return $cmd.Source
    }

    # 2. Check 'py' launcher
    $pyLauncher = Get-Command py -ErrorAction SilentlyContinue
    if ($pyLauncher -and (Test-ValidPython "py")) {
        return "py"
    }

    # 3. Search common installation directories
    $candidatePaths = @(
        "$env:LocalAppData\Programs\Python\Python313\python.exe",
        "$env:LocalAppData\Programs\Python\Python312\python.exe",
        "$env:LocalAppData\Programs\Python\Python311\python.exe",
        "$env:LocalAppData\Programs\Python\Python310\python.exe",
        "C:\Program Files\Python313\python.exe",
        "C:\Program Files\Python312\python.exe",
        "C:\Program Files\Python311\python.exe",
        "C:\Program Files\Python310\python.exe",
        "C:\Python313\python.exe",
        "C:\Python312\python.exe",
        "C:\Python311\python.exe",
        "C:\Python310\python.exe"
    )
    foreach ($p in $candidatePaths) {
        if (Test-ValidPython $p) {
            return $p
        }
    }

    # 4. Registry lookup
    $regPaths = @(
        "HKLM:\SOFTWARE\Python\PythonCore\*\InstallPath",
        "HKCU:\SOFTWARE\Python\PythonCore\*\InstallPath"
    )
    foreach ($regPath in $regPaths) {
        try {
            $items = Get-ItemProperty -Path $regPath -ErrorAction SilentlyContinue
            foreach ($item in $items) {
                if ($item.ExecutablePath -and (Test-ValidPython $item.ExecutablePath)) {
                    return $item.ExecutablePath
                }
                if ($item.'(default)' -and (Test-ValidPython (Join-Path $item.'(default)' "python.exe"))) {
                    return (Join-Path $item.'(default)' "python.exe")
                }
            }
        } catch {}
    }

    return $null
}

function Test-ValidVenv {
    param ([string]$vPyPath)
    if (-not $vPyPath -or -not (Test-Path $vPyPath)) { return $false }
    try {
        $out = & "$vPyPath" -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>&1
        if ($LASTEXITCODE -eq 0 -and $out -match '^(\d+)\.(\d+)') {
            $major = [int]$Matches[1]
            $minor = [int]$Matches[2]
            if ($major -eq 3 -and $minor -ge 10) {
                return $true
            }
        }
    } catch {}
    return $false
}

$script:stage = 0
$script:pythonExe = $null
$script:venvPython = $null

$timer = New-Object System.Windows.Threading.DispatcherTimer
$timer.Interval = [TimeSpan]::FromMilliseconds(150)

$timer.Add_Tick({
    $timer.Stop()

    switch ($script:stage) {
        0 {
            Update-UI 5 "Initializing setup installer..." "System environment initialized."
            $script:stage = 1
            $timer.Interval = [TimeSpan]::FromMilliseconds(300)
            $timer.Start()
        }
        1 {
            Update-UI 10 "Step 1/6: Checking Python installation..." "Locating Python installation (>=3.10)..."
            $pyExe = Get-SystemPythonPath

            if (-not $pyExe) {
                Update-UI 12 "Step 1/6: Downloading Python 3.11 installer..." "Downloading python-3.11.9-amd64.exe..."
                $url = "https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe"
                $installerPath = "$env:TEMP\python-3.11.9-amd64.exe"
                
                $oldProgress = $ProgressPreference
                $ProgressPreference = 'SilentlyContinue'
                try {
                    Invoke-WebRequest -Uri $url -OutFile $installerPath
                } catch {
                    $ProgressPreference = $oldProgress
                    Stop-InstallerWithError 15 "Python download failed." "Unable to download Python installer from python.org. Check network connection."
                    return
                }
                $ProgressPreference = $oldProgress

                Update-UI 16 "Step 1/6: Installing Python 3.11 silently..." "Installing Python 3.11..."
                $proc = Start-Process -FilePath $installerPath -ArgumentList "/quiet InstallAllUsers=0 PrependPath=1 Include_pip=1" -PassThru -Wait
                Remove-Item $installerPath -ErrorAction SilentlyContinue

                # Refresh process environment PATH
                $machinePath = [System.Environment]::GetEnvironmentVariable("Path","Machine")
                $userPath = [System.Environment]::GetEnvironmentVariable("Path","User")
                $userPythonDir = "$env:LocalAppData\Programs\Python\Python311"
                $userScriptsDir = "$env:LocalAppData\Programs\Python\Python311\Scripts"
                $env:PATH = "$userPythonDir;$userScriptsDir;$machinePath;$userPath;$env:PATH"

                $pyExe = Get-SystemPythonPath
            }

            if (-not $pyExe) {
                Stop-InstallerWithError 18 "Python detection failed." "Compatible Python 3.10+ executable was not found. Please install Python manually."
                return
            }

            $script:pythonExe = $pyExe
            Update-UI 20 "Step 1/6: Python verified complete!" "Python executable: $pyExe"
            $script:stage = 2
            $timer.Interval = [TimeSpan]::FromMilliseconds(300)
            $timer.Start()
        }
        2 {
            Update-UI 25 "Step 2/6: Setting up Python virtual environment (venv)..." "Checking virtual environment..."
            $vPy = "$PSScriptRoot\venv\Scripts\python.exe"

            # Check if existing venv is functional on current machine
            $isVenvValid = Test-ValidVenv $vPy

            if (-not $isVenvValid) {
                Update-UI 30 "Step 2/6: Creating fresh virtual environment..." "Executing python -m venv venv..."
                if (Test-Path "$PSScriptRoot\venv") {
                    Remove-Item "$PSScriptRoot\venv" -Recurse -Force -ErrorAction SilentlyContinue
                }

                # Attempt Tier 1: Standard venv creation
                if ($script:pythonExe -eq "py") {
                    & py -3 -m venv "$PSScriptRoot\venv"
                } else {
                    & "$script:pythonExe" -m venv "$PSScriptRoot\venv"
                }

                # Attempt Tier 2: virtualenv fallback if standard venv executable was not created
                if (-not (Test-ValidVenv $vPy)) {
                    Update-UI 35 "Step 2/6: Retrying environment setup with virtualenv..." "Installing virtualenv..."
                    if ($script:pythonExe -eq "py") {
                        & py -3 -m pip install virtualenv --quiet
                        & py -3 -m virtualenv "$PSScriptRoot\venv"
                    } else {
                        & "$script:pythonExe" -m pip install virtualenv --quiet
                        & "$script:pythonExe" -m virtualenv "$PSScriptRoot\venv"
                    }
                }
            }

            # Verify venv executable runs successfully
            if (Test-ValidVenv $vPy) {
                $script:venvPython = $vPy
            } else {
                Stop-InstallerWithError 38 "Virtual environment initialization failed." "Could not create a functional venv Python executable at $vPy."
                return
            }

            Update-UI 40 "Step 2/6: Python environment verified!" "Executable ready: $script:venvPython"
            $script:stage = 3
            $timer.Interval = [TimeSpan]::FromMilliseconds(300)
            $timer.Start()
        }
        3 {
            Update-UI 45 "Step 3/6: Installing Python dependencies..." "Upgrading pip and installing requirements.txt..."
            
            # Upgrade pip silently
            & "$script:venvPython" -m pip install --upgrade pip --quiet 2>&1 | Out-Null

            # Install project requirements
            & "$script:venvPython" -m pip install -r "$PSScriptRoot\requirements.txt" --no-warn-script-location
            if ($LASTEXITCODE -ne 0) {
                Stop-InstallerWithError 50 "Package installation failed." "pip install -r requirements.txt failed with exit code $LASTEXITCODE."
                return
            }

            Update-UI 60 "Step 3/6: Package installation complete!" "Django, PyPDF, Pillow, OpenAI installed."
            $script:stage = 4
            $timer.Interval = [TimeSpan]::FromMilliseconds(300)
            $timer.Start()
        }
        4 {
            Update-UI 65 "Step 4/6: Running database migrations & seeding demo data..." "Running manage.py migrate..."
            & "$script:venvPython" "$PSScriptRoot\manage.py" migrate --noinput
            if ($LASTEXITCODE -ne 0) {
                Stop-InstallerWithError 68 "Database migration failed." "manage.py migrate failed with exit code $LASTEXITCODE."
                return
            }

            Update-UI 70 "Step 4/6: Seeding teacher and student demo accounts..." "Running manage.py seed_demo..."
            & "$script:venvPython" "$PSScriptRoot\manage.py" seed_demo
            if ($LASTEXITCODE -ne 0) {
                Stop-InstallerWithError 72 "Demo data seeding failed." "manage.py seed_demo failed with exit code $LASTEXITCODE."
                return
            }

            Update-UI 75 "Step 4/6: Database setup & demo data complete!" "Database seeded with teacher1 & student1 accounts."
            $script:stage = 5
            $timer.Interval = [TimeSpan]::FromMilliseconds(300)
            $timer.Start()
        }
        5 {
            Update-UI 78 "Step 5/6: Checking Ollama AI engine..." "Verifying local Ollama installation..."
            $ollamaCmd = Get-Command ollama -ErrorAction SilentlyContinue
            $ollamaExe = $null
            if ($ollamaCmd) {
                $ollamaExe = $ollamaCmd.Source
            } else {
                $standardPaths = @(
                    "$env:LocalAppData\Programs\Ollama\ollama.exe",
                    "C:\Program Files\Ollama\ollama.exe"
                )
                foreach ($sp in $standardPaths) {
                    if (Test-Path $sp) { $ollamaExe = $sp; break }
                }
            }

            if (-not $ollamaExe) {
                Update-UI 80 "Step 5/6: Downloading Ollama Windows Installer..." "Downloading OllamaSetup.exe..."
                $ollamaInstaller = "$env:TEMP\OllamaSetup.exe"
                $oldProgress = $ProgressPreference
                $ProgressPreference = 'SilentlyContinue'
                try {
                    Invoke-WebRequest -Uri "https://ollama.com/download/OllamaSetup.exe" -OutFile $ollamaInstaller
                    Update-UI 83 "Step 5/6: Installing Ollama..." "Installing Ollama silently..."
                    Start-Process -FilePath $ollamaInstaller -ArgumentList "/silent" -PassThru -Wait
                    Remove-Item $ollamaInstaller -ErrorAction SilentlyContinue
                } catch {
                    Update-UI 83 "Step 5/6: Downloading Ollama via script..." "Installing Ollama..."
                    try { iex (irm https://ollama.com/install.ps1) } catch {}
                }
                $ProgressPreference = $oldProgress

                # Refresh PATH
                $machinePath = [System.Environment]::GetEnvironmentVariable("Path","Machine")
                $userPath = [System.Environment]::GetEnvironmentVariable("Path","User")
                $env:PATH = "$env:LocalAppData\Programs\Ollama;C:\Program Files\Ollama;$machinePath;$userPath;$env:PATH"
                
                $ollamaCmd = Get-Command ollama -ErrorAction SilentlyContinue
                if ($ollamaCmd) { $ollamaExe = $ollamaCmd.Source }
            }

            # Check if Ollama service is listening
            $ollamaRunning = $false
            try {
                $res = Invoke-RestMethod -Uri "http://localhost:11434/api/tags" -TimeoutSec 3 -ErrorAction SilentlyContinue
                if ($res) { $ollamaRunning = $true }
            } catch {}

            if (-not $ollamaRunning -and $ollamaExe) {
                Update-UI 87 "Step 5/6: Starting local Ollama background worker..." "Starting ollama serve..."
                Start-Process -FilePath $ollamaExe -ArgumentList "serve" -WindowStyle Hidden -ErrorAction SilentlyContinue
                
                for ($i = 0; $i -lt 10; $i++) {
                    Start-Sleep -Seconds 1
                    try {
                        $res = Invoke-RestMethod -Uri "http://localhost:11434/api/tags" -TimeoutSec 2 -ErrorAction SilentlyContinue
                        if ($res) { $ollamaRunning = $true; break }
                    } catch {}
                }
            }

            if ($ollamaRunning) {
                Update-UI 90 "Step 5/6: Ollama AI engine verified & ready!" "Ollama AI service running."
            } else {
                Update-UI 90 "Step 5/6: Ollama offline (Mock AI fallback enabled)" "Ollama service unavailable."
            }

            $script:stage = 6
            $timer.Interval = [TimeSpan]::FromMilliseconds(300)
            $timer.Start()
        }
        6 {
            Update-UI 92 "Step 6/6: Checking Llama 3.2 1B model..." "Verifying Ollama models..."
            $hasModel = $false
            try {
                $res = Invoke-RestMethod -Uri "http://localhost:11434/api/tags" -TimeoutSec 3 -ErrorAction SilentlyContinue
                if ($res -and $res.models) {
                    foreach ($m in $res.models) {
                        if ($m.name -like "*llama3.2:1b*" -or $m.name -like "*llama3.2*") {
                            $hasModel = $true
                            break
                        }
                    }
                }
            } catch {}

            if (-not $hasModel) {
                $ollamaCmd = Get-Command ollama -ErrorAction SilentlyContinue
                if ($ollamaCmd) {
                    Update-UI 94 "Step 6/6: Pulling Llama 3.2 1B model..." "Executing ollama pull llama3.2:1b..."
                    & ollama pull llama3.2:1b 2>&1 | Out-Null
                }
            }

            Update-UI 98 "Step 6/6: AI Model setup complete!" "Llama 3.2 1B model configured."
            $script:stage = 7
            $timer.Interval = [TimeSpan]::FromMilliseconds(500)
            $timer.Start()
        }
        7 {
            Update-UI 99 "Starting application server..." "Launching Django background service on 127.0.0.1:8000..."

            # 1. Start Django server as a persistent background process using verified venv Python
            Start-Process -FilePath $script:venvPython -ArgumentList "`"$PSScriptRoot\manage.py`" runserver 127.0.0.1:8000" -WindowStyle Hidden

            # 2. Poll http://127.0.0.1:8000/ until server responds
            Update-UI 99 "Waiting for application server readiness..." "Connecting to 127.0.0.1:8000..."
            $serverReady = $false
            for ($i = 0; $i -lt 20; $i++) {
                try {
                    $req = [System.Net.WebRequest]::Create("http://127.0.0.1:8000/")
                    $req.Timeout = 1000
                    $res = $req.GetResponse()
                    if ($res) {
                        $serverReady = $true
                        $res.Close()
                        break
                    }
                } catch {
                    if ($_.Exception.Response) {
                        $serverReady = $true
                        break
                    }
                }
                Start-Sleep -Milliseconds 500
            }

            Update-UI 100 "Server ready! Opening application..." "Launching browser..."

            # 3. Open Browser ONLY after server is responsive
            $chromePath = "${env:ProgramFiles}\Google\Chrome\Application\chrome.exe"
            $chromePathx86 = "${env:ProgramFiles(x86)}\Google\Chrome\Application\chrome.exe"

            if (Test-Path $chromePath) {
                Start-Process $chromePath "http://127.0.0.1:8000/"
            } elseif (Test-Path $chromePathx86) {
                Start-Process $chromePathx86 "http://127.0.0.1:8000/"
            } else {
                Start-Process "http://127.0.0.1:8000/"
            }

            # 4. Close installer GUI window
            $window.Close()
        }
    }
})

$window.Add_ContentRendered({
    $timer.Start()
})

$window.ShowDialog() | Out-Null
