#!/bin/bash
set -euo pipefail
echo -e '\e[45m\e[1mBuild script was run.\e[49m\e[39m'
(
    date
    cat input
) > output
