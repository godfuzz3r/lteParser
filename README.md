What is it
=====

The main goal of this project to fastly scan area and retrieve system information blocks of all near cells. This project based on [srsLTE](https://github.com/srsran/srsRAN) (srsRAN since recent time), so it should work with known hardware supported by srsUE (e.g. limesdr, bladerf, usrp)

How it works
=====
1. cell_search tries find cell in specified band, stops at the first cell found
2. srsue tries recover SIB5 from finded cell
3. if srsue can't recover SIB5 at the specified time (default timeout is 30 seconds, configurable), cell_search continues searching valid cell.
4. when SIB's from first cell retrieved, srsue recovers SIB's from neighbohoor cells recursively using SIB5 information
5. all cell's information is saved into postgres database and accessable from web interface


Setup
=====

build with `docker-compose build`
configure your SDR in srsue/ue.conf and `DEVICE_ARGS` env variable in `docker-compose.yml`
plug in your SDR
run `docker-compose up`

Usage
=====

-
