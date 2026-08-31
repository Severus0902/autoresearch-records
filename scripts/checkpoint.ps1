param(
    [Parameter(Mandatory = $true)]
    [string]$Message
)

python -m autoresearch git checkpoint -m $Message

