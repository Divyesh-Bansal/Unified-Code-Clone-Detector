
# Batch configuration: 10 batches of pairs (each batch = 10 pairs = up to 20 unique dirs)
# Last batch has 7 pairs.

$root    = "c:\Users\Pramod\Documents\GitHub\my_tool"
$soco    = Join-Path $root "soco"

# Define all 97 ground-truth pairs grouped into 10 batches of 10 (last = 7)
$batches = @(
    # Batch 1
    @("003","004", "005","006", "008","010", "014","021", "015","023",
      "016","024", "017","022", "030","032", "033","034", "042","044"),
    # Batch 2
    @("043","251", "045","047", "048","051", "048","059", "048","183",
      "048","185", "048","257", "048","258", "049","050", "051","059"),
    # Batch 3
    @("051","183", "051","185", "051","257", "051","258", "052","053",
      "059","183", "059","185", "059","257", "059","258", "061","216"),
    # Batch 4
    @("062","064", "069","070", "078","079", "084","085", "086","087",
      "086","153", "086","155", "086","222", "086","242", "086","243"),
    # Batch 5
    @("087","153", "087","155", "087","222", "087","242", "087","243",
      "089","090", "094","098", "101","212", "103","105", "106","111"),
    # Batch 6
    @("107","108", "107","112", "107","113", "108","112", "108","113",
      "112","113", "117","119", "131","133", "135","174", "136","173"),
    # Batch 7
    @("137","171", "140","142", "143","145", "146","147", "148","150",
      "153","155", "153","222", "153","242", "153","243", "155","222"),
    # Batch 8
    @("155","242", "155","243", "158","161", "159","250", "175","180",
      "181","182", "183","185", "183","257", "183","258", "185","257"),
    # Batch 9
    @("185","258", "188","190", "191","193", "195","218", "201","209",
      "202","208", "211","216", "221","224", "222","242", "222","243"),
    # Batch 10  (7 pairs)
    @("228","230", "232","233", "235","237", "238","240", "242","243",
      "244","246", "257","258")
)

for ($i = 0; $i -lt $batches.Count; $i++) {
    $batchNum  = $i + 1
    $testDir   = Join-Path $root "test$batchNum"
    $reportFile = Join-Path $root "test${batchNum}.txt"

    Write-Host "=== Batch $batchNum ===" -ForegroundColor Cyan

    # Clear the test dir
    if (Test-Path $testDir) {
        Remove-Item -Recurse -Force (Join-Path $testDir "*")
    } else {
        New-Item -ItemType Directory -Path $testDir | Out-Null
    }

    # Collect unique folder IDs from this batch's flat array of pairs
    $ids = $batches[$i] | Select-Object -Unique | Sort-Object

    foreach ($id in $ids) {
        $src = Join-Path $soco $id
        if (Test-Path $src) {
            Copy-Item -Recurse -Force $src (Join-Path $testDir $id)
        } else {
            Write-Warning "SOCO folder not found: $src"
        }
    }

    Write-Host "  Copied $($ids.Count) folders into test$batchNum"

    # Run the tool  (path is a positional argument, --output directs report file)
    Write-Host "  Running tool on test$batchNum ..."
    python -m my_tool $testDir --threshold 60 --mode file --output $reportFile 2>&1
    Write-Host "  Report saved to test${batchNum}.txt"
    Write-Host ""
}

Write-Host "All batches done." -ForegroundColor Green
