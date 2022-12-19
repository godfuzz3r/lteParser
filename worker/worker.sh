#!/bin/bash

## this is environment variables now
#CELL_SEARCH=/srsRAN/build/lib/examples/cell_search
#SRSUE=/srsRAN/build/srsue/src/srsue
#SRSUECFG=/mnt/srsue/ue.conf
#SRSUELOG=/tmp/ue.log
#DEVICE_ARGS="rxant=LNAW"
#RX_GAIN=40
#API=127.0.0.1
#TIMEOUT=30

while true; do
    job=$(curl http://$API:1337/api/job 2>/dev/null)
	if [ "$job" != "null" ]; then
		job_name=$(echo $job | jq -r .job)
		if [ "$job_name" == "cell_search" ]; then
			#nohup $CELL_SEARCH < /dev/null > /tmp/cell_search.log &
			#cell_search_pid=$!
			band=$(echo $job | jq -r .band)
			start_earfcn=$(echo $job | jq -r .start_earfcn)
			end_earfcn=$(echo $job | jq -r .end_earfcn)
			curl http://$API:1337/api/status \
			-H "Content-Type:application/json" --data @<(cat <<EOF
			{
				"status": "ok",
				"name": "cell_search_progress",
				"band": $band,
				"start_earfcn": $start_earfcn,
				"end_earfcn": $end_earfcn
			}
EOF
			)
			$CELL_SEARCH -b $band -s $start_earfcn -e $end_earfcn -a "$DEVICE_ARGS" -g $RX_GAIN | while read line; do
				echo $line
				if grep -q "Found CELL ID" <<< $line; then
					pwait cell_search 2>/dev/null
					earfcn=$(echo $line | awk '{ print $10 }')
					curl http://$API:1337/api/status \
					-H "Content-Type:application/json" --data @<(cat <<EOF
					{
						"status": "ok",
						"name": "cell_search_cell_found",
						"band": $band,
						"current_earfcn": $earfcn,
						"start_earfcn": $start_earfcn,
						"end_earfcn": $end_earfcn
					}
EOF
					)
				fi
				if grep -q "Bye" <<< $line; then
					pwait cell_search
					earfcn=$(echo $line | awk '{ print $10 }')
					curl http://$API:1337/api/status \
					-H "Content-Type:application/json" --data @<(cat <<EOF
					{
						"status": "ok",
						"name": "cell_search_scan_done",
						"band": $band,
						"current_earfcn": $end_earfcn,
						"start_earfcn": $end_earfcn,
						"end_earfcn": $end_earfcn
					}
EOF
					)
				fi
			done
		fi
		if [ "$job_name" == "cell_parse" ]; then
			earfcn=$(echo $job | jq -r .earfcn)
			curl http://$API:1337/api/status \
				-H "Content-Type:application/json" --data @<(cat <<EOF
				{
					"status": "ok",
					"name": "srsue_progress",
					"earfcn": $earfcn
				}
EOF
			)
			echo "connecting to $earfcn"
			rm /tmp/ue.log -f
			$SRSUE $SRSUECFG --log.filename $SRSUELOG --expert.lte_sample_rates=true --rf.device_args "$DEVICE_ARGS" --rf.rx_gain $RX_GAIN --rat.eutra.dl_earfcn $earfcn &
			sibs=$(python3 parse_sib.py -f $SRSUELOG -v -t $TIMEOUT | jq)
			echo $sibs
			pkill srsue
			pwait srsue
			curl http://$API:1337/api/status \
			-H "Content-Type:application/json" --data @<(cat <<EOF
			{
				"status": "ok",
				"name": "srsue_sibs_parsed",
				"current_earfcn": $earfcn,
				"sibs": $sibs
			}
EOF
			)
			rm /mnt/srsue/ue.log
			cp /tmp/ue.log /mnt/srsue/ue.log
			echo "5 sec cooldown for hardware"
			sleep 5
		fi
	fi
	sleep 1
done