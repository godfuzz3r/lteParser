What is it
=====

The main goal of this project to fastly scan area and retrieve system information blocks of all near cells. This project based on [srsLTE](https://github.com/srsran/srsRAN) (srsRAN since recent time), so it should work with known hardware supported by srsUE (e.g. limesdr, bladerf, usrp)

How it works
=====
1. cell_search tries find cell in specified band, stops at the first cell found
2. srsue tries recover sib5 from finded cell
3. if srsue can't recover sib5 at the specified time (default timeout is 10 seconds, configurable), cell_search continues searching valid cell.
4. when sib's from first cell retrieved, srsue recovers sib's from neighbohoor cells recursively using sib5 information (see do_scan () in scan_all.sh)

all retrived sibs save in /tmp/srsue_sibs_acquired/{arfcn}/{sib_index}.json as well as with one resulted json with all information.


Build
=====

```
mkdir build && cd build
cmake .. -DCMAKE_BUILD_TYPE=Debug -DUSE_LTE_RATES=True
make -j8 srsue cell_search
cd ../
mkdir -p binaries
cp build/srsue/src/srsue build/lib/examples/cell_search binaries
```

Usage
=====

`./scan_all.sh -h`
```
scan all frequencies and retrieve sibs recursively

        -b, --band      start band              (default=3)
        -g, --gain      rx gain                 (default=50)
        -a, --args      sdr args                (default='rxant=LNAW')
        -t, --timeout   timeout to get SIBs     (default=10)
        -s, --start     start earfcn            (default all)
        -o, --output                            (default=/tmp/srsue_out.json)
```

To achieve better performance you need to configure scaling governor:
`echo performance | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor`

and run script as root so srsue can run with realtime priority
